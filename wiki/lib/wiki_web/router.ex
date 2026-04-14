defmodule WikiWeb.Router do
  use WikiWeb, :router

  pipeline :browser do
    plug :accepts, ["html"]
    plug :fetch_session
    plug :fetch_live_flash
    plug :put_root_layout, html: {WikiWeb.Layouts, :root}
    plug :protect_from_forgery
    plug :put_secure_browser_headers
  end

  pipeline :api do
    plug :accepts, ["json"]
  end

  scope "/", WikiWeb do
    pipe_through :browser

    live "/", WikiLive, :index
    live "/wiki/*path", WikiLive, :show
  end

  # Other scopes may use custom stacks.
  # scope "/api", WikiWeb do
  #   pipe_through :api
  # end
end
