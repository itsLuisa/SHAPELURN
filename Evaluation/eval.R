
setwd(".")
df <- read.csv("./evaluation_csv/Valentin_evaluation.csv", sep="\t", header=TRUE)
summary(df)

library(ggplot2)

ggplot(df, aes(n, attempts))+
  geom_point()+
  geom_line()+
  geom_smooth(formula=y~x, method=lm, se=FALSE)

lm(attempts~n, df)

#### ATTEMPTS ########
# Bob: Median = 1.000, Mean = 1.216
# Etienne: Median = 1.000, Mean = 1.309
# Katharina: Median = 1.000, Mean = 1.5
# Luisa: Median = 1.000, Mean = 1.057
# Patty S1: Median = 1.000, Mean = 1.204
# Valentin: Median = 1.000, Mean = 1.262