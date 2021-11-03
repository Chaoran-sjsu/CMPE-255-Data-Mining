# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rfe63GLcYYVxl6vc-YIjPe8w0wk1wsLV
"""

import pandas as pd
import numpy as np

from scipy.sparse import csr_matrix

from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import calinski_harabasz_score

from matplotlib import pyplot as plt

#Function for reading file
def csr_read(filename): 
    file = open(filename)
    frequency = list()
    ids = list()
    documents = list()
    count = 0
    for line in file:
        elements = line.strip().split()
        for i in range(0, int(len(elements) / 2)):
            ids.append(int(elements[i * 2]))
            frequency.append(int(elements[i * 2 + 1]))
            documents.append(count)
        count += 1

    return csr_matrix((frequency,(documents, ids)),shape = (8580, 126374),dtype = np.double)

csrMatrix = csr_read('train.dat')

transformer = TfidfTransformer(norm = 'l2', smooth_idf = False)
tfidf = transformer.fit_transform(csrMatrix)

tsvd = TruncatedSVD(n_components = 256)
X_sparse_tsvd = tsvd.fit(csrMatrix).transform(csrMatrix)

#Helper functions for K-means
def Centroids(matrix):
    shuffle(matrix)
    return matrix[:2,:]

def Similarity(matrix, centroids):
    Similarities = matrix.dot(centroids.T)
    return Similarities
    
def Two_Clusters(matrix, centroids):    
    cluster1 = list()
    cluster2 = list()    
    simi_Matrix = Similarity(matrix, centroids)

    for index in range(simi_Matrix.shape[0]):
        simi_Row = simi_Matrix[index]
        simi_Sorted = np.argsort(simi_Row)[-1]

        if simi_Sorted == 0:
            cluster1.append(index)
        else:
            cluster2.append(index)

    return cluster1, cluster2

def Recal_Centroid(matrix, clusters):
    centroids = list()
    
    for i in range(0,2):
        cluster = matrix[clusters[i],:]
        MEAN = cluster.mean(0)
        centroids.append(MEAN)

    centroids_array = np.asarray(centroids)
    return centroids_array

#K-means function
def K_means(matrix, numberOfIterations):    
    centroids = Centroids(matrix)

    for _ in range(numberOfIterations):
        clusters = list()
        cluster1, cluster2 =  (matrix, centroids)
        if len(cluster1) > 1:
            clusters.append(cluster1)
        if len(cluster2) > 1:
            clusters.append(cluster2)
        centroids = Recal_Centroid(matrix, clusters)
    return cluster1, cluster2

#Function for calculating sse 
def SSE(matrix, clusters):  
    SSE_list = list()
    SSE_array = []
    
    for cluster in clusters:
        members = matrix[cluster,:]
        sse = np.sum(np.square(members - np.mean(members)))
        SSE_list.append(sse)
        
    SSE_array = np.asarray(SSE_list)
    dropClusterIndex = np.argsort(SSE_array)[-1]
            
    return dropClusterIndex

#Bisecting K-means function
def bisecting_kmeans(matrix, k, numberOfIterations):
    
    clusters = list()
    
    initialcluster = list()
    for i in range(matrix.shape[0]):
        initialcluster.append(i)
    
    clusters.append(initialcluster)
    
    while len(clusters) < k:

        dropClusterIndex = SSE(matrix, clusters)
        droppedCluster = clusters[dropClusterIndex]
        
        cluster1, cluster2 = K_means(matrix[droppedCluster,:], numberOfIterations)
        del clusters[dropClusterIndex]
        
        actualCluster1 = list()
        actualCluster2 = list()
        for index in cluster1:
            actualCluster1.append(droppedCluster[index])
            
        for index in cluster2:
            actualCluster2.append(droppedCluster[index])
        
        clusters.append(actualCluster1)
        clusters.append(actualCluster2)
    
    labels = [0] * matrix.shape[0]

    for index, cluster in enumerate(clusters):
        for idx in cluster:
            labels[idx] = index + 1
    return labels


#Validate the result
kValues = list()
scores1 = list()
scores2 = list()

for k in range(3, 22, 2):
    labels = bisecting_kmeans(X_sparse_tsvd, k, 10)
    score1 = silhouette_score(X_sparse_tsvd, labels)
    score2 = calinski_harabasz_score(X_sparse_tsvd, labels)
    kValues.append(k)
    scores1.append(score1)
    scores2.append(score2)
    
    print ("K= %d, Silhouette Score is %f" %(k, score1))
    print ("K= %d, Calinski Harabaz Score is %f" %(k, score2))
    
    if (k == 7):
        outputFile = open("output.dat", "w")
        for index in labels:
            outputFile.write(str(index) +'\n')
        outputFile.close()

#plot the validate result
plt.plot(kValues, scores1)
plt.xticks(kValues, kValues)
plt.xlabel('Cluster Number')
plt.ylabel('Silhouette Score')
plt.grid(ls = ':')

plt.show()    
        
plt.plot(kValues, scores2)
plt.xticks(kValues, kValues)
plt.xlabel('Cluster Number')
plt.ylabel('Calinski Harabaz Score')
plt.grid(ls = ':')

plt.show()
