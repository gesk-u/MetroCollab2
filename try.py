import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.cluster import KMeans
import numpy as np

# Example: Your raw data
raw_data = [[
    {'user_firstname': 'Gina', 'user_lastname': 'Garcia', 'skills': '["python", "sql", "javascript", "git", "tableau", "cloud technologies", "blockchain technology"]', 'interests': '["programming", "open source projects", "game development", "complex systems"]', 'availability': '{"mon": ["morning", "afternoon"], "tue": ["morning", "evening"], "wed": ["afternoon", "evening"], "thu": ["morning"], "fri": ["afternoon", "evening"], "weekend": []}', 'hours_per_week': '"10-15"'},
    {'user_firstname': 'Linda', 'user_lastname': 'Johnson', 'skills': '["python", "bash scripting", "docker", "kubernetes", "aws cloud services", "automation", "devops practices"]', 'interests': '["devops practices", "machine learning", "blockchain technology"]', 'availability': '{"mon": ["morning", "afternoon"], "tue": ["morning", "evening"], "wed": ["afternoon", "evening"], "thu": ["morning", "afternoon"], "fri": ["morning", "evening"], "weekend": []}', 'hours_per_week': '"10-15"'},
    {'user_firstname': 'William', 'user_lastname': 'Hines', 'skills': '["python", "bash scripting", "docker containerization", "ansible", "terraform", "ci/cd pipelines", "aws", "cryptographic applications"]', 'interests': '["cybersecurity", "penetration testing", "threat analysis", "blockchain technology", "smart contract development"]', 'availability': '{"mon": ["morning", "afternoon"], "tue": ["evening"], "wed": ["morning", "afternoon"], "thu": ["evening"], "fri": ["morning", "afternoon"], "weekend": []}', 'hours_per_week': '"5-10"'},
    {'user_firstname': 'Cody', 'user_lastname': 'Cooper', 'skills': '["python", "r", "sql", "data manipulation", "statistical modeling", "machine learning", "tensorflow", "pandas"]', 'interests': '["machine learning", "virtual reality", "cloud technologies", "devops", "software solutions"]', 'availability': '{"mon": ["morning", "afternoon"], "tue": ["evening"], "wed": ["morning", "afternoon"], "thu": ["evening"], "fri": ["morning", "afternoon"], "weekend": []}', 'hours_per_week': '"20+"'},
    {'user_firstname': 'Lisa', 'user_lastname': 'Wright', 'skills': '["python", "docker", "kubernetes", "terraform", "devops automation", "cloud infrastructure management"]', 'interests': '["devops", "cloud infrastructure", "mobile applications", "responsive user interface development"]', 'availability': '{"mon": ["morning", "afternoon"], "tue": ["evening"], "wed": ["morning", "afternoon"], "thu": ["evening"], "fri": ["morning", "afternoon"], "weekend": []}', 'hours_per_week': '"20+"'},
    {'user_firstname': 'Gary', 'user_lastname': 'Guerrero', 'skills': '["python", "java", "go", "docker", "kubernetes", "terraform", "ansible", "devops", "automation", "system management"]', 'interests': '["machine learning", "blockchain development", "vr experiences"]', 'availability': '{"mon": ["morning", "afternoon"], "tue": ["morning", "evening"], "wed": ["afternoon", "evening"], "thu": ["morning", "afternoon"], "fri": ["morning", "evening"], "weekend": []}', 'hours_per_week': '"15-20"'},
    {'user_firstname': 'Jessica', 'user_lastname': 'Wallace', 'skills': '["python", "sql database design", "mysql", "postgresql", "data analysis", "aws", "devops"]', 'interests': '["game design", "cybersecurity", "threat detection", "machine learning"]', 'availability': '{"mon": ["morning", "afternoon"], "tue": ["morning", "evening"], "wed": ["afternoon", "evening"], "thu": ["morning", "afternoon"], "fri": ["morning", "evening"], "weekend": []}', 'hours_per_week': '"20+"'},
    {'user_firstname': 'Monica', 'user_lastname': 'Oliver', 'skills': '["python", "tensorflow", "pytorch", "machine learning", "ai solutions"]', 'interests': '["machine learning", "internet of things", "cloud technologies", "scalable applications"]', 'availability': '{"mon": ["morning", "afternoon"], "tue": ["morning", "evening"], "wed": ["afternoon", "evening"], "thu": ["morning", "afternoon"], "fri": ["morning", "evening"], "weekend": []}', 'hours_per_week': '"10-15"'},
    {'user_firstname': 'Jose', 'user_lastname': 'Gregory', 'skills': '["python", "sql", "aws", "data analysis", "machine learning algorithms"]', 'interests': '["web development", "machine learning"]', 'availability': '{"mon": ["morning", "afternoon"], "tue": ["morning", "evening"], "wed": ["afternoon", "evening"], "thu": ["morning", "afternoon"], "fri": ["morning", "evening"], "weekend": []}', 'hours_per_week': '"20+"'},
    {'user_firstname': 'Laura', 'user_lastname': 'Page', 'skills': '["python", "java", "sql", "git"]', 'interests': '["developing applications", "blockchain technology", "open source projects"]', 'availability': '{"mon": ["morning", "afternoon"], "tue": ["morning", "evening"], "wed": ["afternoon", "evening"], "thu": ["morning", "afternoon"], "fri": ["morning", "evening"], "weekend": []}', 'hours_per_week': '"15-20"'}
]]

users = raw_data[0]


# Step 1: Parse the inner JSON fields
for rec in users:
    rec['skills'] = json.loads(rec['skills'])
    rec['interests'] = json.loads(rec['interests'])
    rec['availability'] = json.loads(rec['availability'])
    rec['hours_per_week'] = json.loads(rec['hours_per_week'])

# Step 2: Prepare features

# Flatten availability into a list of "day-time" strings, e.g. "mon_morning"
def flatten_availability(avail_dict):
    slots = []
    for day, periods in avail_dict.items():
        for period in periods:
            slots.append(f"{day}_{period}")
    return slots

avail_lists = [flatten_availability(rec['availability']) for rec in users]
skills_lists = [rec['skills'] for rec in users]
interests_lists = [rec['interests'] for rec in users]

# Encode skills, interests, availability with MultiLabelBinarizer (one-hot encode sets)
mlb_skills = MultiLabelBinarizer()
skills_encoded = mlb_skills.fit_transform(skills_lists)

mlb_interests = MultiLabelBinarizer()
interests_encoded = mlb_interests.fit_transform(interests_lists)

mlb_avail = MultiLabelBinarizer()
avail_encoded = mlb_avail.fit_transform(avail_lists)

# Encode hours_per_week: map ranges to numeric bins
hours_map = {
    "5-10": 1,
    "10-15": 2,
    "15-20": 3,
    "20+": 4
}
hours_encoded = np.array([hours_map.get(rec['hours_per_week'], 0) for rec in users]).reshape(-1, 1)

# Step 3: Combine all features into a single feature matrix
features = np.hstack([skills_encoded, interests_encoded, avail_encoded, hours_encoded])

# Step 4: Cluster (e.g., into 3 groups)
k = 4
kmeans = KMeans(n_clusters=k, random_state=42)
labels = kmeans.fit_predict(features)
labels = np.array(labels)
centers = kmeans.cluster_centers_

MIN_SIZE = 2
MAX_SIZE = 3

def cluster_sizes(labels):
    """Return dict {cluster: count}"""
    unique, counts = np.unique(labels, return_counts=True)
    return dict(zip(unique, counts))


# Step 5: Add cluster label back to records
for rec, label in zip(users, labels):
    rec['group'] = int(label) + 1


# ---------------------------------------------------------
# 1) Fix groups that are too small (< MIN_SIZE)
# ---------------------------------------------------------
sizes = cluster_sizes(labels)

small_clusters = [c for c, s in sizes.items() if s < MIN_SIZE]

for sc in small_clusters:
    idxs = np.where(labels == sc)[0]

    for idx in idxs:
        dists = np.linalg.norm(features[idx] - centers, axis=1)

        # try nearest clusters in ascending distance
        for target in np.argsort(dists):
            if target != sc:
                # check target group not exceeding max size
                if sizes[target] < MAX_SIZE:
                    labels[idx] = target
                    sizes[target] += 1
                    sizes[sc] -= 1
                    break


# ---------------------------------------------------------
# 2) Fix groups that are too large (> MAX_SIZE)
# ---------------------------------------------------------
sizes = cluster_sizes(labels)

large_clusters = [c for c, s in sizes.items() if s > MAX_SIZE]

for lc in large_clusters:
    idxs = np.where(labels == lc)[0]

    # number of extra members
    overflow = sizes[lc] - MAX_SIZE

    # sort members by how weakly they belong to the cluster
    dists = [np.linalg.norm(features[i] - centers[lc]) for i in idxs]
    sorted_idxs = [x for _, x in sorted(zip(dists, idxs), reverse=True)]

    for idx in sorted_idxs[:overflow]:
        # Try nearest new cluster
        dists_to_centers = np.linalg.norm(features[idx] - centers, axis=1)

        for target in np.argsort(dists_to_centers):
            if target != lc and sizes[target] < MAX_SIZE:
                labels[idx] = target
                sizes[target] += 1
                sizes[lc] -= 1
                break


# ---------------------------------------------------------
# 3) Assign final labels back to user records
# ---------------------------------------------------------
for rec, label in zip(users, labels):
    rec['group'] = int(label)


# Now raw_data contains group assignments
for rec in users:
    print(f"{rec['user_firstname']} {rec['user_lastname']} -> Group {rec['group']}")