"""
Checkpoint/Rollback Manager for IDFWU Orchestration
Creates state snapshots before agent wave execution and supports rollback on failure.
Checkpoints stored in .force/checkpoints/ within the target project.
"""

import hashlib
import json
import logging
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_CHECKPOINT_DIR = Path(__file__).resolve().parent.parent.parent / ".force" / "checkpoints"


class Checkpoint:
    """Represents a point-in-time snapshot of project state."""

    def __init__(self, checkpoint_id: str, wave: int, stories: List[str], files: Dict[str, str]):
        self.checkpoint_id = checkpoint_id
        self.wave = wave
        self.stories = stories
        self.files = files  # path -> content hash
        self.created_at = datetime.utcnow().isoformat()
        self.status = "created"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "wave": self.wave,
            "stories": self.stories,
            "files": self.files,
            "created_at": self.created_at,
            "status": self.status,
        }


class CheckpointManager:
    """Manages checkpoint creation, storage, and rollback."""

    def __init__(self, checkpoint_dir: Optional[Path] = None):
        self.checkpoint_dir = checkpoint_dir or DEFAULT_CHECKPOINT_DIR
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir = self.checkpoint_dir / "snapshots"
        self.snapshots_dir.mkdir(exist_ok=True)

    def create_checkpoint(
        self, wave: int, stories: List[str], target_files: List[str]
    ) -> Checkpoint:
        """
        Create a state snapshot before agent wave execution.

        Args:
            wave: Wave number being executed
            stories: List of story IDs in this wave
            target_files: List of file paths that will be modified

        Returns:
            Checkpoint object with metadata
        """
        checkpoint_id = f"cp-wave{wave}-{int(time.time())}"
        snapshot_dir = self.snapshots_dir / checkpoint_id
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        file_hashes = {}
        for file_path in target_files:
            p = Path(file_path)
            if p.exists():
                content = p.read_bytes()
                file_hash = hashlib.sha256(content).hexdigest()[:12]
                file_hashes[file_path] = file_hash

                # Store backup copy
                backup_path = snapshot_dir / p.name
                shutil.copy2(file_path, backup_path)

                # Store path mapping
                mapping_file = snapshot_dir / "file_mapping.json"
                mapping = {}
                if mapping_file.exists():
                    mapping = json.loads(mapping_file.read_text())
                mapping[file_path] = str(backup_path)
                mapping_file.write_text(json.dumps(mapping, indent=2))
            else:
                file_hashes[file_path] = "new_file"

        checkpoint = Checkpoint(checkpoint_id, wave, stories, file_hashes)

        # Write checkpoint metadata
        meta_path = self.checkpoint_dir / f"{checkpoint_id}.json"
        meta_path.write_text(json.dumps(checkpoint.to_dict(), indent=2))

        logger.info(f"Checkpoint {checkpoint_id} created: {len(file_hashes)} files snapshotted")
        return checkpoint

    def rollback(self, checkpoint_id: str) -> bool:
        """
        Rollback file state to a checkpoint.

        Args:
            checkpoint_id: ID of checkpoint to restore

        Returns:
            True if rollback succeeded
        """
        snapshot_dir = self.snapshots_dir / checkpoint_id
        mapping_file = snapshot_dir / "file_mapping.json"

        if not mapping_file.exists():
            logger.error(f"Checkpoint {checkpoint_id} not found or has no file mapping")
            return False

        mapping = json.loads(mapping_file.read_text())
        restored = 0

        for original_path, backup_path in mapping.items():
            try:
                if Path(backup_path).exists():
                    shutil.copy2(backup_path, original_path)
                    restored += 1
                    logger.info(f"Restored: {original_path}")
                else:
                    logger.warning(f"Backup missing for {original_path}")
            except Exception as e:
                logger.error(f"Failed to restore {original_path}: {e}")

        # Update checkpoint metadata
        meta_path = self.checkpoint_dir / f"{checkpoint_id}.json"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text())
            meta["status"] = "rolled_back"
            meta["rolled_back_at"] = datetime.utcnow().isoformat()
            meta_path.write_text(json.dumps(meta, indent=2))

        logger.info(f"Rollback {checkpoint_id}: {restored}/{len(mapping)} files restored")
        return restored == len(mapping)

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List all checkpoints with metadata."""
        checkpoints = []
        for meta_file in sorted(self.checkpoint_dir.glob("cp-*.json")):
            try:
                checkpoints.append(json.loads(meta_file.read_text()))
            except (json.JSONDecodeError, OSError):
                continue
        return checkpoints

    def cleanup(self, keep_last: int = 5) -> int:
        """Remove old checkpoints, keeping the most recent N."""
        checkpoints = sorted(
            self.checkpoint_dir.glob("cp-*.json"),
            key=lambda p: p.stat().st_mtime,
        )
        removed = 0
        for meta_file in checkpoints[:-keep_last] if len(checkpoints) > keep_last else []:
            cp_id = meta_file.stem
            snapshot_dir = self.snapshots_dir / cp_id
            if snapshot_dir.exists():
                shutil.rmtree(snapshot_dir)
            meta_file.unlink()
            removed += 1
        return removed
