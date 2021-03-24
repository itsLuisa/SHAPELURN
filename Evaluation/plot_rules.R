#################################
## FILE TO PLOT AVERAGE RULE
################################
library(ggplot2)

## Summarizes data.
## Gives count, mean, standard deviation, standard error of the mean, and confidence interval (default 95%).
##   data: a data frame.
##   measurevar: the name of a column that contains the variable to be summariezed
##   groupvars: a vector containing names of columns that contain grouping variables
##   na.rm: a boolean that indicates whether to ignore NA's
##   conf.interval: the percent range of the confidence interval (default is 95%)

summarySE <- function(data=NULL, measurevar, groupvars=NULL, na.rm=FALSE,
                      conf.interval=.95, .drop=TRUE) {
  require(plyr)
  
  # New version of length which can handle NA's: if na.rm==T, don't count them
  length2 <- function (x, na.rm=FALSE) {
    if (na.rm) sum(!is.na(x))
    else       length(x)
  }
  
  # This does the summary. For each group's data frame, return a vector with
  # N, mean, and sd
  datac <- ddply(data, groupvars, .drop=.drop,
                 .fun = function(xx, col) {
                   c(N    = length2(xx[[col]], na.rm=na.rm),
                     mean = mean   (xx[[col]], na.rm=na.rm),
                     sd   = sd     (xx[[col]], na.rm=na.rm)
                   )
                 },
                 measurevar
  )
  
  # Rename the "mean" column    
  datac <- rename(datac, c("mean" = measurevar))
  
  datac$se <- datac$sd / sqrt(datac$N)  # Calculate standard error of the mean
  
  # Confidence interval multiplier for standard error
  # Calculate t-statistic for confidence interval: 
  # e.g., if conf.interval is .95, use .975 (above/below), and use df=N-1
  ciMult <- qt(conf.interval/2 + .5, datac$N-1)
  datac$ci <- datac$se * ciMult
  
  return(datac)
}

#### START EVALUATION ################################

setwd(".")
setwd("C:/Users/Katharina/Documents/Studium/Master/Language Action and Perception/Project/Analyse")
data <- read.table("rules_3levels.csv", sep="\t", header=TRUE)

str(data)

data$Subject <- as.factor(data$Subject)

### PLOT WITHOUT CONFIDENCE INTEVALS

l1.means <- mean(data$Level1_averaged)

l2.means <- mean(data$Level2_averaged)

l3.means <- mean(data$Level3_averaged)

all_means <- c(l1.means, l2.means, l3.means)      

levels <- c("1", "2", "3")

d_means <- data.frame(all_means, levels)


ggplot(d_means, aes(levels, all_means, group = 1))+
  geom_point() +
  geom_line() +
  ylab("Average number") + 
  xlab("Level") +
  ggtitle("Average Number of Potential Rules per Word \n at End of each Level") + 
  theme(plot.title = element_text(hjust = 0.5,        
                                  size = 10)) 
# save plot as png
pname <- paste("Plot_rules_per_word", "png", sep = ".")
ggsave(pname, height=3, width=5, bg="white")


#### PLOT WITH ERROR BARS ####################

summ_l1 <- summarySE(data, "Level1_averaged")
summ_l2 <- summarySE(data, "Level2_averaged")
summ_l3 <- summarySE(data, "Level3_averaged")

all_means <- c(summ_l1$Level1_averaged, summ_l2$Level2_averaged, summ_l3$Level3_averaged)

all_ci <- c(summ_l1$ci, summ_l2$ci, summ_l3$ci)

levels <- c("1", "2", "3")

d_means <- data.frame(all_means, all_ci, levels)

ggplot(d_means, aes(levels, all_means, group = 1))+
  geom_point() +
  geom_line() +
  geom_errorbar(aes(group = 1,
                    ymin = all_means - all_ci,
                    ymax = all_means + all_ci),
                width=0.25,
                position=position_dodge(0)) +
  ylab("Average number") + 
  xlab("Level") +
  ggtitle("Average Number of Potential Rules per Word \n at End of each Level") + 
  theme(plot.title = element_text(hjust = 0.5,        
                                  size = 10)) 
# save plot as png
pname <- paste("Plot_rules_per_word_with_CI", "png", sep = ".")
ggsave(pname, height=3, width=5, bg="white")
