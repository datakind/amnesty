AmnestyApp::Application.routes.draw do
  resources :amnesties


  get "static/index"

  resources :amnesties
  root :to => 'static#index'
end
