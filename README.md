# 🌌 Cosmos 1.0: A Multidimensional Map of the Emerging Technology Frontier

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Status](https://img.shields.io/badge/status-active-success)

## 📄 Overview

**Cosmos 1.0** is an open dataset and analysis framework for identifying and mapping emerging technologies using large-scale text data from Wikipedia, OpenAlex, Google Scholar, and Crunchbase. This repository includes:

- **📊 ET23k Dataset:** A collection of **23,544 emerging technologies** classified into **hierarchical clusters**.
- **🌍 ET100:** A curated list of **100 emerging technologies** with significant academic and industrial recognition.
- **📈 Technology Indices:** Four key indices to analyze awareness, generality, deeptech potential, and technology age.
- **🧑‍💻 Machine Learning-Based Approach:** Uses **Wikipedia2Vec embeddings**, **hierarchical clustering**, and **statistical validation**.
- **📂 Publicly Available Data:** All code and data are openly accessible for research and industry applications.

---

## 📂 Repository Structure

```plaintext
├── data/
│   ├── Cosmos_Dataset.csv         # Full dataset (ET23k)
│   ├── ET100_List.csv             # Subset of 100 emerging technologies
│   ├── technology_indices.csv     # Computed indices (Awareness, Deeptech, etc.)
│   ├── metadata/                  # Additional metadata (e.g., Wikipedia links)
├── notebooks/
│   ├── 01_Data_Exploration.ipynb  # Initial data exploration
│   ├── 02_Clustering_Analysis.ipynb  # Hierarchical clustering
│   ├── 03_Index_Validation.ipynb  # Index validation and comparison
├── src/
│   ├── data_processing.py         # Scripts for preprocessing Wikipedia data
│   ├── clustering.py              # Hierarchical clustering methods
│   ├── index_computation.py       # Computation of technology indices
├── figures/                        # Plots and visualizations
├── README.md                       # This README file
└── LICENSE                         # License file

