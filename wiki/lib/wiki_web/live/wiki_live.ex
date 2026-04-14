defmodule WikiWeb.WikiLive do
  use WikiWeb, :live_view

  alias Wiki.WikiStore

  @impl true
  def mount(_params, _session, socket) do
    toc = WikiStore.get_toc()

    socket =
      socket
      |> assign(:page_title, "IDFW Wiki")
      |> assign(:toc, toc)
      |> assign(:search_query, "")
      |> assign(:search_results, nil)
      |> assign(:current_slug, nil)
      |> assign(:doc_html, nil)
      |> assign(:doc_title, nil)
      |> assign(:chat_open, false)
      |> assign(:chat_messages, [])

    {:ok, socket}
  end

  @impl true
  def handle_params(params, _uri, socket) do
    slug = case params do
      %{"path" => parts} when is_list(parts) -> Enum.join(parts, "/")
      _ -> "index"
    end

    case WikiStore.get_page(slug) do
      nil ->
        {:noreply, assign(socket, current_slug: slug, doc_html: nil, doc_title: "Not Found")}
      page ->
        {:noreply,
         assign(socket,
           current_slug: slug,
           doc_html: page.html,
           doc_title: page.title,
           page_title: "#{page.title} - IDFW Wiki"
         )}
    end
  end

  @impl true
  def handle_event("search", %{"query" => query}, socket) do
    if String.trim(query) == "" do
      {:noreply, assign(socket, search_query: "", search_results: nil)}
    else
      results = WikiStore.search(query)
      {:noreply, assign(socket, search_query: query, search_results: results)}
    end
  end

  def handle_event("toggle_chat", _params, socket) do
    {:noreply, assign(socket, chat_open: !socket.assigns.chat_open)}
  end

  @impl true
  def render(assigns) do
    ~H"""
    <div class="flex h-screen bg-base-300 overflow-hidden">
      <%!-- Sidebar --%>
      <aside class="w-64 bg-base-200 border-r border-base-300 flex flex-col flex-shrink-0">
        <div class="p-4 border-b border-base-300">
          <h1 class="text-lg font-bold text-primary flex items-center gap-2">
            <span class="inline-block w-2 h-2 rounded-full bg-success animate-pulse"></span>
            IDFW Wiki
          </h1>
          <p class="text-xs text-base-content/50 mt-1">IDEA Definition Framework</p>
        </div>

        <%!-- Search --%>
        <div class="p-3 border-b border-base-300">
          <form phx-change="search" phx-submit="search">
            <input
              type="text"
              name="query"
              value={@search_query}
              placeholder="Search wiki..."
              class="input input-sm input-bordered w-full"
              phx-debounce="300"
            />
          </form>
        </div>

        <%!-- Search Results or TOC --%>
        <nav class="flex-1 overflow-y-auto p-2 space-y-1">
          <%= if @search_results do %>
            <div class="text-xs text-base-content/50 px-2 mb-1">
              {@search_results |> length()} results
            </div>
            <%= for {slug, title} <- @search_results do %>
              <.link
                navigate={if slug == "index", do: ~p"/", else: ~p"/wiki/#{slug}"}
                class={"block px-3 py-1.5 rounded text-sm hover:bg-base-300 #{if @current_slug == slug, do: "bg-primary/10 text-primary font-medium", else: "text-base-content/70"}"}
              >
                {title}
              </.link>
            <% end %>
          <% else %>
            <%= for {section, pages} <- @toc do %>
              <div class="mt-3 first:mt-0">
                <div class="text-xs font-semibold text-base-content/40 uppercase tracking-wider px-3 mb-1">
                  {section}
                </div>
                <%= for {slug, title, _} <- pages do %>
                  <.link
                    navigate={if slug == "index", do: ~p"/", else: ~p"/wiki/#{slug}"}
                    class={"block px-3 py-1.5 rounded text-sm hover:bg-base-300 #{if @current_slug == slug, do: "bg-primary/10 text-primary font-medium", else: "text-base-content/70"}"}
                  >
                    {title}
                  </.link>
                <% end %>
              </div>
            <% end %>
          <% end %>
        </nav>

        <%!-- Footer --%>
        <div class="p-3 border-t border-base-300">
          <div class="text-xs text-base-content/40">
            <a href="http://localhost:3031" target="_blank" class="hover:text-primary">APM Dashboard</a>
            <span class="mx-1">|</span>
            <button phx-click="toggle_chat" class="hover:text-primary">Chat</button>
          </div>
        </div>
      </aside>

      <%!-- Main Content --%>
      <main class="flex-1 overflow-y-auto">
        <div class="max-w-4xl mx-auto p-8">
          <%= if @doc_html do %>
            <article class="prose prose-sm max-w-none
              prose-headings:text-base-content prose-p:text-base-content/80
              prose-a:text-primary prose-strong:text-base-content
              prose-code:text-secondary prose-pre:bg-base-200">
              {Phoenix.HTML.raw(@doc_html)}
            </article>
          <% else %>
            <div class="text-center py-20">
              <h2 class="text-2xl font-bold text-base-content/50">Page Not Found</h2>
              <p class="text-base-content/30 mt-2">The page "{@current_slug}" does not exist yet.</p>
            </div>
          <% end %>
        </div>
      </main>

      <%!-- Chat Sidebar --%>
      <%= if @chat_open do %>
        <aside class="w-80 bg-base-200 border-l border-base-300 flex flex-col">
          <div class="p-3 border-b border-base-300 flex items-center justify-between">
            <span class="font-semibold text-sm">Wiki Chat</span>
            <button phx-click="toggle_chat" class="btn btn-ghost btn-xs">x</button>
          </div>
          <div class="flex-1 overflow-y-auto p-3">
            <div class="text-xs text-base-content/40 text-center py-8">
              Chat assistant coming soon. Connect via LiveView channel.
            </div>
          </div>
          <div class="p-3 border-t border-base-300">
            <input type="text" placeholder="Ask about IDFW..." class="input input-sm input-bordered w-full" disabled />
          </div>
        </aside>
      <% end %>
    </div>
    """
  end
end
