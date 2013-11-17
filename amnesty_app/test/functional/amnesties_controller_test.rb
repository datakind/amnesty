require 'test_helper'

class AmnestiesControllerTest < ActionController::TestCase
  setup do
    @amnesty = amnesties(:one)
  end

  test "should get index" do
    get :index
    assert_response :success
    assert_not_nil assigns(:amnesties)
  end

  test "should get new" do
    get :new
    assert_response :success
  end

  test "should create amnesty" do
    assert_difference('Amnesty.count') do
      post :create, amnesty: {  }
    end

    assert_redirected_to amnesty_path(assigns(:amnesty))
  end

  test "should show amnesty" do
    get :show, id: @amnesty
    assert_response :success
  end

  test "should get edit" do
    get :edit, id: @amnesty
    assert_response :success
  end

  test "should update amnesty" do
    put :update, id: @amnesty, amnesty: {  }
    assert_redirected_to amnesty_path(assigns(:amnesty))
  end

  test "should destroy amnesty" do
    assert_difference('Amnesty.count', -1) do
      delete :destroy, id: @amnesty
    end

    assert_redirected_to amnesties_path
  end
end
