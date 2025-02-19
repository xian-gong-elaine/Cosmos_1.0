library(ggplot2)
library(ggridges)
library(viridis)
library(tidyverse)

df <- read.csv('Datasets/Ridgeline_Technology.csv')

df <- df %>%
  mutate(Cluster = fct_relevel(Cluster, levels = 'Data & Analytics', 'Networking & Connectivity', 'Nanotechnology', 
                              'Autonomous Systems', 'Health & Medical', 'Converging Technology', 'Biotechnology'))

p <- ggplot(df, aes(Date, Wiki_Entity, height = Pageviews, group = Wiki_Entity)) +
  geom_density_ridges(aes(fill= Cluster), stat = "identity", scale = 1.5, alpha=0.3, show.legend = TRUE) +
  scale_fill_manual(name = "ET7 theme clusters", guide = "legend",
                    values = c("#E7298A", "#A6761D", "#E6AB02", "#1B9E77", "#66A61E", "#7570B3", "#D95F02")) +
  #scale_color_cyclical(name = "ET7 theme clusters", guide = "legend",
  #                     values = c('Data & Analytics', 'Networking & Connectivity', 'Nanotechnology', 
  #                                'Autonomous Systems', 'Health & Medical', 'Converging Technology', 
  #                                'Biotechnology')) + 
  #scale_fill_viridis(option = "G", alpha = 0.6) +
  theme_ridges(grid = FALSE, center_axis_labels = TRUE) + 
  theme(axis.title.x=element_blank(),
        axis.title.y=element_blank(),
        legend.key.size = unit(0.4, 'cm'),
        #axis.text.x = element_text(angle = 45, hjust = 1),
        legend.margin =margin(r=10,l=5,t=5,b=10),
        text=element_text(size=10),
        axis.text=element_text(size=10),
        legend.position="bottom",
        legend.title=element_blank()) +
  #scale_x_continuous(breaks=c(202100, 202200, 202300, 202400), labels = c('2021','2022','2023','2024'))
  #theme(axis.text.x = element_text(angle = 90, hjust = 1)) + 
  scale_x_discrete(breaks=c('2021-01', '2022-01', '2023-01', '2024-01'), 
                   labels = c('Jan 2021', 'Jan 2022', 'Jan 2023', 'Jan 2024')) + 
  scale_y_discrete(limits = c('Microbial electrosynthesis', 'Phenomics', 'Continuous glucose monitor', 
                              'Unconventional computing', 'Optical neural network', 'Egocentric vision', 
                              'Electronic data capture', 'Cognitive behavioral therapy for insomnia', 
                              'Enterprise master patient index', 'Electronic navigational chart', 
                              'GNSS reflectometry', 'Snapshot hyperspectral imaging', 'Quantum sensor', 
                              'Superconducting quantum computing', 'Photonic integrated circuit', 
                              'Network emulation', 'Post-quantum cryptography', 'Real-time communication', 
                              'Multi-agent system', 'Generative model', 'Echo state network'))

show(p)

# Save the plot as a PDF
ggsave("Monthly_Pageviews_Trend.pdf", plot = p, width = 10, height = 10)
