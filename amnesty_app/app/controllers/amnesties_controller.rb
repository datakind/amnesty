class AmnestiesController < ApplicationController
  # GET /amnesties
  # GET /amnesties.json
  def index
    @amnesties = Amnesty.all

    respond_to do |format|
      format.html # index.html.erb
      format.json { render json: @amnesties }
    end
  end

  # GET /amnesties/1
  # GET /amnesties/1.json
  def show
    @amnesty = Amnesty.find(params[:id])

    respond_to do |format|
      format.html # show.html.erb
      format.json { render json: @amnesty }
    end
  end

  # GET /amnesties/new
  # GET /amnesties/new.json
  def new
    @amnesty = Amnesty.new

    respond_to do |format|
      format.html # new.html.erb
      format.json { render json: @amnesty }
    end
  end

  # GET /amnesties/1/edit
  def edit
    @amnesty = Amnesty.find(params[:id])
  end

  # POST /amnesties
  # POST /amnesties.json
  def create
    @amnesty = Amnesty.new(params[:amnesty])

    respond_to do |format|
      if @amnesty.save
        format.html { redirect_to @amnesty, notice: 'Amnesty was successfully created.' }
        format.json { render json: @amnesty, status: :created, location: @amnesty }
      else
        format.html { render action: "new" }
        format.json { render json: @amnesty.errors, status: :unprocessable_entity }
      end
    end
  end

  # PUT /amnesties/1
  # PUT /amnesties/1.json
  def update
    @amnesty = Amnesty.find(params[:id])

    respond_to do |format|
      if @amnesty.update_attributes(params[:amnesty])
        format.html { redirect_to @amnesty, notice: 'Amnesty was successfully updated.' }
        format.json { head :no_content }
      else
        format.html { render action: "edit" }
        format.json { render json: @amnesty.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /amnesties/1
  # DELETE /amnesties/1.json
  def destroy
    @amnesty = Amnesty.find(params[:id])
    @amnesty.destroy

    respond_to do |format|
      format.html { redirect_to amnesties_url }
      format.json { head :no_content }
    end
  end
end
