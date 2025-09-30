# FFForce GLP Visualizer

This project provides a Python tool to explore **Goodlift Points (GLP)** distributions in **FFForce weight categories**.  
It allows interactive visualization of athlete performance, including search by name and statistical context.

## Features

- Histogram of GLP scores for each weight class  
- Gaussian curve fitted to the distribution  
- Athlete search by name (accent-insensitive)  
- Displays:
  - Rank within the category  
  - Total  
  - Percentile  
  - Z-score  
- Radio buttons to select **sex** and **weight class**  
- Built with `matplotlib` and `scipy`

## Requirements

- Python 3.10+  
- matplotlib  
- scipy  
- pandas  

Install dependencies with:

```bash
pip install -r requirements.txt
