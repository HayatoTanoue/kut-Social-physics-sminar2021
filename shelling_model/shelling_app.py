import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from shelling import Schelling

# Streamlit App

st.title("Schelling Model simulation")

col1, col2 = st.beta_columns(2)
population_size = col1.slider("居住容量", 500, 2500, 1000)
empty_ratio = col1.slider("空き地割合", 0.2, 0.9, 0.3)
similarity_threshold = col1.slider("閾値", 0.0, 1.0, 0.4)

see_range = col2.slider("view range (何マスまでを隣人とするか)", min_value=1, max_value=10, value=1)
n_move = col2.number_input(
    "num move (移動住民数/iter)", value=100, max_value=500, min_value=10
)
n_iterations = col2.number_input("Number of Iterations", value=10, min_value=2)

schelling = Schelling(
    population_size, empty_ratio, similarity_threshold, see_range, 0.002
)

mean_similarity_ratio = []
mean_similarity_ratio.append(schelling.get_mean_similarity_ratio())

# Plot the graphs at initial stage
plt.style.use("ggplot")
plt.figure(figsize=(8, 4))

# Left hand side graph with Schelling simulation plot
cmap = ListedColormap(["k", "lightBlue", "w"])
plt.subplot(121)
plt.axis("off")
plt.pcolor(schelling.city, cmap=cmap, edgecolors="w", linewidths=1)

# Right hand side graph with Mean Similarity Ratio graph
plt.subplot(122)
plt.xlabel("Iterations")
plt.xlim([0, n_iterations])
plt.ylim([0.4, 1])
plt.title("Mean Similarity Ratio", fontsize=15)
plt.text(
    1,
    0.95,
    "Similarity Ratio: %.4f" % schelling.get_mean_similarity_ratio(),
    fontsize=10,
)

city_plot = st.pyplot(plt)
progress_bar = st.progress(0)

if col2.button("Run Simulation"):

    for i in range(n_iterations):
        for _ in range(3):
            schelling.run(n_move)
        mean_similarity_ratio.append(schelling.get_mean_similarity_ratio())
        plt.figure(figsize=(8, 4))

        plt.subplot(121)
        plt.axis("off")
        plt.pcolor(schelling.city, cmap=cmap, edgecolors="w", linewidths=1)

        plt.subplot(122)
        plt.xlabel("Iterations")
        plt.xlim([0, n_iterations])
        plt.ylim([0.4, 1])
        plt.title("Mean Similarity Ratio", fontsize=15)
        plt.plot(range(1, len(mean_similarity_ratio) + 1), mean_similarity_ratio)
        plt.text(
            1,
            0.95,
            "Similarity Ratio: %.4f" % schelling.get_mean_similarity_ratio(),
            fontsize=10,
        )

        city_plot.pyplot(plt)
        plt.close("all")
        progress_bar.progress((i + 1.0) / n_iterations)