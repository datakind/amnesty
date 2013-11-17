AmnestyApp::Application.routes.draw do
  get "static/index"

  resources :amnesties
  root :to => 'static#index'
end
