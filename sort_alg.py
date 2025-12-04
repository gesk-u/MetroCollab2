import json
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.cluster import KMeans
import gensim.downloader as api

def sort_groups(min_group, max_group, users_data):
    
    users = users_data  
    
    # Parse the inner JSON
    for rec in users:
        rec['skills'] = json.loads(rec['skills'])
        rec['interests'] = json.loads(rec['interests'])
        rec['availability'] = json.loads(rec['availability'])
        rec['hours_per_week'] = rec['hours_per_week'].strip('"')
    
    # flatten availability into "day_period" strings
    def flatten_availability(avail_dict):
        slots = []
        for day, periods in avail_dict.items():
            for period in periods:
                slots.append(f"{day}_{period}")
        return slots
    
    avail_lists = [flatten_availability(rec['availability']) for rec in users]
    
    # Load pre-trained GloVe embedding
    print("Loading GloVe model (this might take a minute)...")
    w2v_model = api.load("glove-wiki-gigaword-100")
    
    # Helper to compute average embedding
    def average_embedding(words, model):
        vecs = []
        for w in words:
            parts = w.lower().split()
            part_vecs = [model[word] for word in parts if word in model]
            if part_vecs:
                vecs.append(np.mean(part_vecs, axis=0))
        if vecs:
            return np.mean(vecs, axis=0)
        else:
            return np.zeros(model.vector_size)
    
    # skill embeddings for each user
    skill_embeddings = np.array([average_embedding(rec['skills'], w2v_model) for rec in users])
    
    # interests and availability
    mlb_interests = MultiLabelBinarizer()
    interests_encoded = mlb_interests.fit_transform([rec['interests'] for rec in users])
    
    mlb_avail = MultiLabelBinarizer()
    avail_encoded = mlb_avail.fit_transform(avail_lists)
    
    # hours per week
    hours_map = {"5-10": 1, "10-15": 2, "15-20": 3, "20+": 4}
    hours_encoded = np.array([hours_map.get(rec['hours_per_week'], 0) for rec in users]).reshape(-1, 1)
    
    #  combine all features
    features = np.hstack([skill_embeddings, interests_encoded, avail_encoded, hours_encoded])
    
    # Optimal number of groups
    n_users = len(users)
    MIN_SIZE = min_group 
    MAX_SIZE = max_group 
    
    # Find valid configurations
    def find_valid_group_configuration(n_users, min_size, max_size):
        """Find a valid configuration of group sizes."""
        # Try different numbers of groups
        for n_groups in range(n_users // max_size, n_users // min_size + 1):
            # Try to distribute users
            base_size = n_users // n_groups
            remainder = n_users % n_groups
            
            # Check if we can distribute the remainder
            if base_size >= min_size and base_size <= max_size:
                if remainder == 0:
                    return n_groups, [base_size] * n_groups
                elif base_size + 1 <= max_size and remainder <= n_groups:
                    sizes = [base_size] * n_groups
                    for i in range(remainder):
                        sizes[i] += 1
                    return n_groups, sizes
        
        # If does not work: use a greedy approach
        sizes = []
        remaining = n_users
        while remaining > 0:
            if remaining >= min_size * 2:  # Can make another group after this
                size = min(max_size, remaining - min_size)
            else:
                size = remaining
            sizes.append(size)
            remaining -= size
        return len(sizes), sizes
    
    n_groups, target_sizes = find_valid_group_configuration(n_users, MIN_SIZE, MAX_SIZE)
    print(f"Target configuration: {n_groups} groups with sizes {target_sizes}")
    
    # Starting clustering
    kmeans = KMeans(n_clusters=n_groups, random_state=42, n_init=10)
    initial_labels = kmeans.fit_predict(features)
    centers = kmeans.cluster_centers_
    
    # balanced assignment algorithm
    def balanced_assignment(features, centers, target_sizes):
        """Assign users to groups while respecting size constraints."""
        n_samples = len(features)
        n_clusters = len(centers)
        
        # Euclidean distance from each student to each cluster center
        distances = np.array([[np.linalg.norm(features[i] - centers[j]) 
                            for j in range(n_clusters)] 
                            for i in range(n_samples)])
        
        # Beginning assignments
        assignments = np.full(n_samples, -1, dtype=int)
        cluster_counts = np.zeros(n_clusters, dtype=int)
        
        # Create a list of (user_idx, cluster_idx, distance) for all pairs
        all_assignments = []
        for i in range(n_samples):
            for j in range(n_clusters):
                all_assignments.append((i, j, distances[i, j]))
        
        # Sort by distance (best matches first)
        all_assignments.sort(key=lambda x: x[2])
        
        # Assign users greedily based on best matches
        for user_idx, cluster_idx, distance in all_assignments:
            # Check if user is already assigned
            if assignments[user_idx] >= 0:
                continue
            
            # Check if cluster has space
            if cluster_counts[cluster_idx] < target_sizes[cluster_idx]:
                assignments[user_idx] = cluster_idx
                cluster_counts[cluster_idx] += 1
        
        # Verify all users are assigned (they should be i hope)
        unassigned = np.where(assignments == -1)[0]
        if len(unassigned) > 0:
            print(f"Warning: {len(unassigned)} users unassigned, forcing assignment")
            for user_idx in unassigned:
                for cluster_idx in range(n_clusters):
                    if cluster_counts[cluster_idx] < target_sizes[cluster_idx]:
                        assignments[user_idx] = cluster_idx
                        cluster_counts[cluster_idx] += 1
                        break
        
        return assignments
    
    # apply balanced assignment
    final_labels = balanced_assignment(features, centers, target_sizes)
    
    # assign to users and create groups
    for rec, label in zip(users, final_labels):
        rec['group'] = int(label) + 1  # Groups start at 1
    
    # Create groups dictionary with user IDs
    groups = {}
    for rec in users:
        group_num = rec['group']
        if group_num not in groups:
            groups[group_num] = []
        groups[group_num].append(rec['id'])  # Store user ID
    
    #print("\nGroup assignments:")
    #print(groups)
    return groups
