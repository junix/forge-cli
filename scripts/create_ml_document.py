#!/usr/bin/env python
"""
Script to create a document object from machine learning guide text,
with each main section as a separate chunk.
"""

import hashlib
import re
from typing import Any

from _types import Chunk
from common.logger import logger
from doc import Document, DocumentContent

# The complex document text from navigator_page.py
complex_document = """
# Machine Learning Comprehensive Guide

## 1. Introduction to Machine Learning
Machine learning is a subset of artificial intelligence that provides systems the ability
to learn and improve from experience without being explicitly programmed.
It focuses on developing computer programs that can access data and use it to learn for themselves.

The process of learning begins with observations or data, such as examples, direct experience,
or instruction, in order to look for patterns in data and make better decisions in the future
based on the examples we provide.

## 2. Types of Machine Learning

### 2.1 Supervised Learning
Supervised learning is the machine learning task of learning a function that maps an input to
an output based on example input-output pairs. It infers a function from labeled training data
consisting of a set of training examples.

#### 2.1.1 Classification
Classification is the problem of identifying to which category an observation belongs.
Examples include email spam detection, image recognition, and customer churn prediction.

Common classification algorithms include:
- Logistic Regression
- Support Vector Machines
- Decision Trees and Random Forests
- Neural Networks
- Naive Bayes classifiers

#### 2.1.2 Regression
Regression is used to predict continuous values rather than discrete categories.
Examples include price prediction, age estimation, and weather forecasting.

Common regression algorithms include:
- Linear Regression
- Polynomial Regression
- Ridge and Lasso Regression
- Elastic Net
- Support Vector Regression

### 2.2 Unsupervised Learning
Unsupervised learning is the machine learning task of inferring a function to describe hidden
structure from unlabeled data. The system doesn't figure out the right output, but explores
the data and can draw inferences from datasets.

#### 2.2.1 Clustering
Clustering is the task of grouping a set of objects in such a way that objects in the same
group are more similar to each other than to those in other groups.

Common clustering algorithms include:
- K-means clustering
- Hierarchical clustering
- DBSCAN
- Gaussian Mixture Models

#### 2.2.2 Dimensionality Reduction
Dimensionality reduction is the process of reducing the number of random variables under
consideration by obtaining a set of principal variables.

Common dimensionality reduction techniques include:
- Principal Component Analysis (PCA)
- t-Distributed Stochastic Neighbor Embedding (t-SNE)
- Autoencoders
- Linear Discriminant Analysis (LDA)

### 2.3 Reinforcement Learning
Reinforcement learning is an area concerned with how software agents ought to take actions
in an environment in order to maximize some notion of cumulative reward.

#### 2.3.1 Key Concepts
- Agent: The program that makes decisions
- Environment: The world in which the agent operates
- Action: The moves made by the agent
- Reward: Feedback from the environment
- Policy: Strategy for selecting actions

#### 2.3.2 Common Algorithms
- Q-Learning
- Deep Q Networks (DQN)
- Policy Gradient Methods
- Actor-Critic Methods

## 3. Evaluation Metrics

### 3.1 Classification Metrics
- Accuracy: Proportion of correct predictions
- Precision: Proportion of positive identifications that were actually correct
- Recall: Proportion of actual positives that were identified correctly
- F1 Score: Harmonic mean of precision and recall
- ROC Curve and AUC: Measures discrimination ability

### 3.2 Regression Metrics
- Mean Absolute Error (MAE)
- Mean Squared Error (MSE)
- Root Mean Squared Error (RMSE)
- R-squared (Coefficient of Determination)

## 4. Model Selection and Optimization

### 4.1 Cross-Validation
Cross-validation is a technique used to evaluate predictive models by partitioning the
original sample into a training set to train the model, and a test set to evaluate it.

### 4.2 Hyperparameter Tuning
Hyperparameter tuning is the problem of choosing a set of optimal hyperparameters for a
learning algorithm. Common techniques include:
- Grid Search
- Random Search
- Bayesian Optimization

### 4.3 Regularization
Regularization is a technique used to prevent overfitting by adding a penalty term to the loss function.
Common regularization techniques include:
- L1 Regularization (Lasso)
- L2 Regularization (Ridge)
- Dropout (for neural networks)
- Early Stopping
"""


def extract_sections(text: str) -> list[dict[str, Any]]:
    """
    Extract only main sections from the text based on '## ' markdown headers.
    Only extracts top-level sections (e.g., ## 1. Introduction) not subsections (### 2.1).

    Args:
        text: The document text

    Returns:
        List of dictionaries with section title and content
    """
    # Strip leading/trailing whitespace
    text = text.strip()

    # First, extract the title (# heading)
    title_match = re.search(r"^# (.+)$", text, re.MULTILINE)
    title = title_match.group(1) if title_match else "Untitled Document"

    # Find all level 2 headers (## headers) which mark main sections
    # Only match headers that start with ## followed by a number, ignoring subsection numbering (e.g., 2.1)
    section_matches = list(re.finditer(r"## (\d+)\. (.+)", text))

    sections = []

    # Process each section
    for i, match in enumerate(section_matches):
        section_start = match.start()
        section_number = match.group(1)
        section_title = match.group(2)

        # Determine section end (either next section or end of text)
        if i < len(section_matches) - 1:
            section_end = section_matches[i + 1].start()
        else:
            section_end = len(text)

        # Extract section content including the header
        section_content = text[section_start:section_end].strip()

        sections.append(
            {"title": section_title, "content": section_content, "index": i, "section_number": int(section_number)}
        )

    return sections, title


def create_document() -> Document:
    """
    Create a Document object with main sections as chunks.

    Returns:
        Document: The created document object
    """
    # Extract main sections from the text
    sections, title = extract_sections(complex_document)

    # Create chunks for each main section
    chunks = []
    for section in sections:
        chunk = Chunk(
            content=section["content"],
            index=section["index"],
            metadata={"title": section["title"], "section_number": section["section_number"]},
        )
        chunks.append(chunk)

    # Calculate MD5 hash of the document
    doc_md5 = hashlib.md5(complex_document.encode()).hexdigest()

    # Create DocumentContent object
    doc_content = DocumentContent(
        id=doc_md5,
        segments=chunks,
        summary=f"Comprehensive guide covering {len(sections)} main areas of Machine Learning",
        tags=["machine learning", "AI", "guide"],
        language="en",
        file_type="markdown",
    )

    # Create and return the Document object
    document = Document(md5sum=doc_md5, mime_type="text/markdown", content=doc_content, title=title)

    return document


def main():
    """Main function to create and display the document"""
    # Create the document
    document = create_document()

    # Log document details
    logger.info(f"Created document: {document.title}")
    logger.info(f"Document ID: {document.id}")
    logger.info(f"MD5: {document.md5sum}")

    # Log chunk details
    logger.info(f"Document has {len(document.content.segments)} chunks:")
    for i, chunk in enumerate(document.content.segments):
        logger.info(f"Chunk {i + 1}: {chunk.metadata.get('title')}")
        logger.info(f"  - Token count: {chunk.estimate_tokens()}")
        logger.info(f"  - Content preview: {chunk.content[:50]}...")

    # Return the document for further use if needed
    return document


if __name__ == "__main__":
    main()
