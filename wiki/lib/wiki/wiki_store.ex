defmodule Wiki.WikiStore do
  @moduledoc "In-memory wiki content store with markdown rendering."

  use Agent

  def start_link(_opts) do
    Agent.start_link(fn -> load_pages() end, name: __MODULE__)
  end

  def get_toc do
    Agent.get(__MODULE__, fn pages ->
      pages
      |> Enum.map(fn {slug, page} -> {slug, page.title, page.section} end)
      |> Enum.sort_by(fn {_, _, section} -> section end)
      |> Enum.group_by(fn {_, _, section} -> section end)
    end)
  end

  def get_page(slug) do
    Agent.get(__MODULE__, fn pages -> Map.get(pages, slug) end)
  end

  def search(query) do
    q = String.downcase(query)
    Agent.get(__MODULE__, fn pages ->
      pages
      |> Enum.filter(fn {_slug, page} ->
        String.contains?(String.downcase(page.title), q) ||
        String.contains?(String.downcase(page.markdown), q)
      end)
      |> Enum.map(fn {slug, page} -> {slug, page.title} end)
    end)
  end

  defp load_pages do
    content_dir = Path.join(:code.priv_dir(:wiki), "wiki_content")

    if File.dir?(content_dir) do
      content_dir
      |> File.ls!()
      |> Enum.filter(&String.ends_with?(&1, ".md"))
      |> Enum.into(%{}, fn filename ->
        slug = String.trim_trailing(filename, ".md")
        path = Path.join(content_dir, filename)
        markdown = File.read!(path)
        {title, section} = extract_metadata(markdown)
        {:ok, html, _} = Earmark.as_html(markdown)
        {slug, %{title: title, section: section, markdown: markdown, html: html}}
      end)
    else
      %{}
    end
  end

  defp extract_metadata(markdown) do
    lines = String.split(markdown, "\n", parts: 5)
    title = case Enum.find(lines, &String.starts_with?(&1, "# ")) do
      nil -> "Untitled"
      line -> String.trim_leading(line, "# ")
    end
    section = case Enum.find(lines, &String.starts_with?(&1, "<!-- section: ")) do
      nil -> "General"
      line ->
        line
        |> String.trim_leading("<!-- section: ")
        |> String.trim_trailing(" -->")
    end
    {title, section}
  end
end
