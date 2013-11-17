## Codifying the countries into ISO3 codes. 

# setwd("")  # set to local working directory 

# install.packages("countrycode")
library(countrycode) # this package codes strings into ISO3c codes. 

ai <- read.csv("../cleaned_data/lotus_database.csv") # loading data. 

# Cleaning the database country column into ISO3 -> https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3

iso3_country <- countrycode(ai$country, "country.name", "iso3c") # Coding into ISO3. 
iso3_subject <- countrycode(ai$subject, "country.name", "iso3c") # Coding into ISO3. 
iso3_category <- countrycode(ai$category, "country.name", "iso3c") # Coding into ISO3. 

total <- length(iso3_country)

iso3 <- iso3_country 
print(sprintf("%s/%s are missing after using country field...",sum(is.na(iso3)), total))
iso3[is.na(iso3)] <- iso3_subject[is.na(iso3)]
print(sprintf("%s/%s are missing after using subject field...",sum(is.na(iso3)), total))
iso3[is.na(iso3)] <- iso3_category[is.na(iso3)] 
print(sprintf("%s/%s are missing after using category field...",sum(is.na(iso3)), total))

ai2 <- cbind(ai, iso3) # Adding columns (the safe way). 
print("...done!")
write.csv(ai2, file="../cleaned_data/lotus_database_w_iso3.csv") # output.