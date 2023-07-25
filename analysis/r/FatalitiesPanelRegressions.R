library(AER)
library(plm)
data(Fatalities)

Fatalities<- pdata.frame(Fatalities, index = c("state", "year"))

is.data.frame(Fatalities)

dim(Fatalities)
# str(Fatalities)
head(Fatalities)

summary(Fatalities[, c(1, 2)])

# Define "fatility rate"
Fatalities$fatal_rate <- Fatalities$fatal / Fatalities$pop * 10000

# subset the data
Fatalities1982 <- subset(Fatalities, year == "1982")
Fatalities1988 <- subset(Fatalities, year == "1988")

# Estimate simple regression using 1982 and 1988 data
fatal1982_mod <- lm(fatal_rate ~ beertax, data = Fatalities1982)
fatal1988_mod <- lm(fatal_rate ~ beertax, data = Fatalities1988)

coeftest(fatal1982_mod, vcov. = vcovHC, type="HC1")
coeftest(fatal1988_mod, vcov. = vcovHC, type="HC1")

# plot the observations and add the estimated regression line for 1982 data
plot(x = as.double(Fatalities1982$beertax), 
     y = as.double(Fatalities1982$fatal_rate), 
     xlab = "Beer tax (in 1988 dollars)",
     ylab = "Fatality rate (fatalities per 10000)",
     main = "Traffic Fatality Rates and Beer Taxes in 1982",
     ylim = c(0, 4.5),
     pch = 20, 
     col = "steelblue")

abline(fatal1982_mod, lwd = 1.5)

# plot observations and add estimated regression line for 1988 data
plot(x = as.double(Fatalities1988$beertax), 
     y = as.double(Fatalities1988$fatal_rate), 
     xlab = "Beer tax (in 1988 dollars)",
     ylab = "Fatality rate (fatalities per 10000)",
     main = "Traffic Fatality Rates and Beer Taxes in 1988",
     ylim = c(0, 4.5),
     pch = 20, 
     col = "steelblue")

abline(fatal1988_mod, lwd = 1.5)


# computer the differences
diff_fatal_rate <- Fatalities1988$fatal_rate - Fatalities1982$fatal_rate
diff_beertax <- Fatalities1988$beertax - Fatalities1982$beertax

# estimate regression using differenced beta
fatal_diff_mod <- lm(diff_fatal_rate ~ diff_beertax)
coeftest(fatal_diff_mod, vcov = vcovHC, type = "HC1")

# plot the differenced data
plot(x = as.double(diff_beertax), 
     y = as.double(diff_fatal_rate), 
     xlab = "Change in beer tax (in 1988 dollars)",
     ylab = "Change in fatality rate (fatalities per 10000)",
     main = "Changes in Traffic Fatality Rates and Beer Taxes in 1982-1988",
     xlim = c(-0.6, 0.6),
     ylim = c(-1.5, 1),
     pch = 20, 
     col = "steelblue")

# add the regression line to plot
abline(fatal_diff_mod, lwd = 1.5)

fatal_fe_lm_mod <- lm(fatal_rate ~ beertax + state - 1, data=Fatalities)
fatal_fe_lm_mod

# obtain demeaned data
Fatalities_demeaned <- with(Fatalities,
                            data.frame(fatal_rate = fatal_rate - ave(fatal_rate, state),
                                       beertax = beertax - ave(beertax, state)))

# estimate the regression
summary(lm(fatal_rate ~ beertax - 1, data = Fatalities_demeaned))

# estimate the fixed effects regression with plm()
fatal_fe_mod <- plm(fatal_rate ~ beertax, 
                    data = Fatalities,
                    index = c("state", "year"), 
                    model = "within")


coeftest(fatal_fe_mod, vcov. = vcovHC, type = "HC1")


# estimate a combined time AND entity fixed effects regression model

# via lm()
fatal_tefe_lm_mod <- lm(fatal_rate ~ beertax + state + year - 1, data = Fatalities)
fatal_tefe_lm_mod


# via plm()
fatal_tefe_mod <- plm(fatal_rate ~ beertax, 
                      data = Fatalities,
                      index = c("state", "year"), 
                      model = "within", 
                      effect = "twoways")

coeftest(fatal_tefe_mod, vcov = vcovHC, type = "HC1")

class(Fatalities$state)
class(Fatalities$year)
