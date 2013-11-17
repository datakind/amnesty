class AmnestiesController < ActionController::Base

	def new
		@amnesty = Amnesty.new
	end

	def create
		@amnesty = Amnesty.create(params[:amnesty])
		if @amnesty.save
      # redirect_to need a route
    else
      render :new
    end
	end

	def edit
		@amnesty = Amnesty.find(params[:id])
	end

	def update
		@amnesty = Amnesty.find(params[:id])
	  if @amnesty.update_attributes(params[:amnesty])
			flash[:notice] = 'User info was updated!'
		else
			render :edit
		end
	end
end
