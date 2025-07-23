import matplotlib.pyplot as plt
import numpy as np
import re

def showPlot(st, response_lower):
    if "confusion matrix" in response_lower:
        st.markdown("### 📊 Sample Confusion Matrix")

        # Try to extract numbers (4 values expected)
        numbers = [int(n) for n in re.findall(r'\b\d+\b', st.session_state.last_answer)]
        if len(numbers) >= 4:
            cm = np.array([[numbers[0], numbers[1]], [numbers[2], numbers[3]]])
        else:
            cm = np.array([[50, 10], [5, 35]])

        fig, ax = plt.subplots()
        ax.matshow(cm, cmap='Blues')
        for (i, j), val in np.ndenumerate(cm):
            ax.text(j, i, f'{val}', ha='center', va='center')
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        st.pyplot(fig)

    # Accuracy Plot
    elif "accuracy plot" in response_lower or "training accuracy" in response_lower:
        st.markdown("### 📈 Training Accuracy Over Epochs")

        # Try to extract float accuracy values from response (e.g., 0.7, 0.85, etc.)
        accuracy_matches = [float(n) for n in re.findall(r"\b0\.\d+\b|\b1\.0\b", st.session_state.last_answer)]

        if len(accuracy_matches) >= 3:
            accuracy = np.array(accuracy_matches[:10])
            epochs = np.arange(1, len(accuracy) + 1)
        else:
            epochs = np.arange(1, 11)
            accuracy = np.clip(np.linspace(0.5, 0.95, 10) + np.random.normal(0, 0.02, 10), 0.5, 1.0)

        fig, ax = plt.subplots()
        ax.plot(epochs, accuracy, marker='o', color='green')
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Accuracy")
        ax.set_title("Model Accuracy Over Time")
        ax.grid(True)
        st.pyplot(fig)