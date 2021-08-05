import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st
from network_shelling import Network_Schelling


def draw(G, pos, ax, nodesize=False):
    num_to_color = {0: "w", 1: "springgreen", -1: "yellow"}
    if nodesize:
        nodesize = [G.degree(i) * 25 for i in range(nx.number_of_nodes(G))]
    else:
        nodesize = None

    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=nodesize,
        node_color=[
            num_to_color[G.nodes[i]["kind"]] for i in range(nx.number_of_nodes(G))
        ],
        ax=ax,
    )

    nx.draw_networkx_edges(G, pos, edge_color="grey", alpha=0.4, ax=ax)
    ax.grid(False)
    ax.set_facecolor("k")


def app():
    st.title("network shelling model simulation")

    col1, col2 = st.beta_columns(2)
    num_nodes = col1.slider("number of nodes", 100, 500, 100)
    empty_ratio = col1.slider("空き地割合", 0.1, 0.5, 0.2)
    similarity_threshold = col1.slider("閾値", 0.0, 1.0, 0.4)

    k = col1.slider("反発係数", min_value=0.1, max_value=2.0, value=0.15)

    parameter = col2.slider("parameter", min_value=1, max_value=10, value=1)

    n_move = col2.number_input(
        "num move (移動住民数/iter)", value=10, max_value=300, min_value=10
    )
    n_iterations = col2.number_input("Number of Iterations", value=10, min_value=2)

    node_deg = col2.radio("node size", [True, False], index=1)

    schelling = Network_Schelling(
        num_nodes, parameter, empty_ratio, similarity_threshold, 0.002
    )

    mean_similarity_ratio = []
    mean_similarity_ratio.append(schelling.get_mean_similarity_ratio())

    # Plot the graphs at initial stage
    plt.style.use("ggplot")
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # Left hand side graph with Schelling simulation plot
    pos = nx.spring_layout(schelling.G, k=k)
    draw(schelling.G, pos, axes[0], node_deg)

    # Right hand side graph with Mean Similarity Ratio graph
    axes[1].set_xlabel("Iterations")
    axes[1].set_xlim([0, n_iterations])
    axes[1].set_ylim([0.4, 1])
    axes[1].set_title("Mean Similarity Ratio", fontsize=15)
    axes[1].text(
        1,
        0.95,
        "Similarity Ratio: %.4f" % schelling.get_mean_similarity_ratio(),
        fontsize=10,
    )

    city_plot = st.pyplot(fig)
    # city_plot = st.pyplot(fig)
    progress_bar = st.progress(0)

    if col2.button("Run Simulation"):

        for i in range(n_iterations):
            schelling.run(n_move)
            mean_similarity_ratio.append(schelling.get_mean_similarity_ratio())

            fig, axes = plt.subplots(1, 2, figsize=(12, 6))

            # Left hand side graph with Schelling simulation plot
            draw(schelling.G, pos, axes[0], node_deg)

            # Right hand side graph with Mean Similarity Ratio graph
            axes[1].set_xlabel("Iterations")
            axes[1].set_xlim([0, n_iterations])
            axes[1].set_ylim([0.4, 1])
            axes[1].set_title("Mean Similarity Ratio", fontsize=15)
            axes[1].text(
                1,
                0.95,
                "Similarity Ratio: %.4f" % schelling.get_mean_similarity_ratio(),
                fontsize=10,
            )
            axes[1].plot(
                range(1, len(mean_similarity_ratio) + 1), mean_similarity_ratio
            )
            city_plot.pyplot(fig)
            plt.close("all")

            progress_bar.progress((i + 1.0) / n_iterations)
