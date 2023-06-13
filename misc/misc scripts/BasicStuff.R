library(dplyr)

df <- read.csv('startup_url_list.csv')
random_rows <- df %>% sample_n(40)
write.csv(random_rows, "url_samples.csv")
