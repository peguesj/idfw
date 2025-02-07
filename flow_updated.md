```plantuml
@startwsd "IDEA Process"
title User provides an idea/prompt

participant User
participant IDPG as "IDPG (Prompt & Generation)"
participant IDPC as "IDPC (Project Config)"
participant SDREF as "SDREF (Standard References)"
participant DDD as "DDD (Default Docs/Diagrams)"
participant IDFW as "IDFW (Master Spec & Actions)"
participant Logger as "Logger (Activity Logging)"

User -> IDPG: Provide idea/prompt

alt Referencing IDFPJ or custom steps?
    IDPG -> IDFW: Retrieve matching IDFPJ
else
    IDPG -> IDPG: Proceed with custom flows
end

IDPG -> IDPC: Load/check config for API keys, tools, environment, security

alt Multi-axis constraints?
    IDPC -> IDPC: Incorporate/check axisDefinitions
    alt Auto-generate masterAxis?
        IDPC -> IDPC: Create masterAxis from config
    else
        IDPC -> IDPC: Use default/none
    end
else
    IDPC -> IDPC: No multi-axis constraints
end

IDPG -> SDREF: Check for standard doc types
SDREF -> SDREF: Map to formatType or generatorId

IDPG -> DDD: Pull default template if no custom format
DDD -> DDD: Retrieve default generator if needed

IDPG -> IDFW: Assemble docs, diagrams, variables, versionControl
IDFW -> IDFW: Invoke projectActions

alt actionType == "generate"
    IDFW -> IDFW: Create new doc/diagram
else
    alt actionType == "update"
        IDFW -> IDFW: Modify existing doc/diagram
    else
        alt actionType == "remove"
            IDFW -> IDFW: Remove specified artifact
        else
            IDFW -> IDFW: Reference existing artifact
        end
    end
end

IDFW -> Logger: Log action in versionControl
Logger -> Logger: Store/log artifact in versionControl

User -> IDPG: Combine all into final output
@endwsd
``` 
