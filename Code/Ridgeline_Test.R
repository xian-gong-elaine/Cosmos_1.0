library(ggplot2)
library(ggridges)
library(viridis)
library(dplyr)

df <- read.csv('Datasets/Ridgeline_Technology.csv')

ggplot(df, aes(Date, Wiki_Entity, height = Pageviews, group = Wiki_Entity)) +
  geom_density_ridges_gradient(aes(fill= ..y..), stat = "identity", scale = 1.5, alpha=0.6, show.legend = FALSE) +
  scale_fill_viridis(option = "G", alpha = 0.6) +
  theme_ridges(grid = FALSE, center_axis_labels = TRUE) + 
  theme(axis.title.x=element_blank(),
        axis.title.y=element_blank()) +
  #scale_x_continuous(breaks=c(202100, 202200, 202300, 202400), labels = c('2021','2022','2023','2024')) +
  #theme(axis.text.x = element_text(angle = 90, hjust = 1)) + 
  scale_x_discrete(breaks=c('2021-01', '2022-01', '2023-01', '2024-01'), 
                   labels = c('Jan 2021', 'Jan 2022', 'Jan 2023', 'Jan 2024'))+
  scale_y_discrete(limits = c('Microbial electrosynthesis', 'Phenomics', 'Continuous glucose monitor', 
                              'Unconventional computing', 'Optical neural network', 'Egocentric vision', 
                              'Applied ontology', 'Cognitive behavioral therapy for insomnia', 
                              'Enterprise master patient index', 'Electronic navigational chart', 
                              'GNSS reflectometry', 'Snapshot hyperspectral imaging', 'Quantum sensor', 
                              'Superconducting quantum computing', 'Photonic integrated circuit', 
                              'Network emulation', 'Post-quantum cryptography', 'Real-time communication', 
                              'Multi-agent system', 'Generative model', 'Echo state network'))

set.seed(3467)

df<- data.frame(method= c(rep("A", 1000), rep("B", 1000), rep("C", 1000)), 
                beta=c(rnorm(1000, mean=0, sd=1),rnorm(1000, mean=2, sd=1.4),rnorm(1000, mean=0, sd=0.5)))

df <- df %>%
  mutate(method = fct_relevel(method, levels = "B", "C", "A"))

  