
from sklearn.cluster import KMeans


class TeamAssigner:
    def __init__(self):
        self.team_colors = {}
        self.players_team_dict = {}


    def get_clustering_model(self, image):
        #reshape image in 2d array of pixels
        image_2d = image.reshape(-1, 3)

        #perform kmeans clustering
        kmeans = KMeans(n_clusters=2, init = "k-means++", n_init=10).fit(image_2d)
        kmeans.fit(image_2d)
        return kmeans

    def get_player_color(self, frame, bbox):
        image = frame[int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])]

        top_half_image = image[0:int(image.shape[0]/2), :]

        #get clustering model

        kmeans = self.get_clustering_model(top_half_image)

        #get the cluster labels for each pixel
        labels = kmeans.labels_

        #Reshape the labels back to the original image shape
        clustered_image = labels.reshape(top_half_image.shape[0], top_half_image.shape[1])

        # get the player cluster

        corner_clusters = [clustered_image[0,0], clustered_image[0,-1], clustered_image[-1,0], clustered_image[-1,-1]]
        non_player_cluster = max(set(corner_clusters), key=corner_clusters.count)

        player_cluster = 1 - non_player_cluster

        player_color = kmeans.cluster_centers_[player_cluster]

        return player_color

    def assign_teams(self, frame, player_detections):

        player_colors = []
        for _, player_detection in player_detections.items():
            bbox = player_detection["bbox"]
            player_color = self.get_player_color(frame, bbox)
            player_colors.append(player_color)


        kmeans = KMeans(n_clusters=2, init="k-means++", n_init=10)
        kmeans.fit(player_colors)

        self.kmeans = kmeans

        # Assign colors so Team 1 is always the white team (higher brightness)
        cluster_0_brightness = sum(kmeans.cluster_centers_[0])
        cluster_1_brightness = sum(kmeans.cluster_centers_[1])

        if cluster_0_brightness > cluster_1_brightness:
            # Cluster 0 is white, no swap needed
            self.team_colors[1] = kmeans.cluster_centers_[0]
            self.team_colors[2] = kmeans.cluster_centers_[1]
            self.clusters_swapped = False
        else:
            # Cluster 1 is white, need to swap
            self.team_colors[1] = kmeans.cluster_centers_[1]
            self.team_colors[2] = kmeans.cluster_centers_[0]
            self.clusters_swapped = True

        self.white_team_id = 1

    def get_player_team(self, frame, player_bbox, player_id):
        if player_id in self.players_team_dict:
            return self.players_team_dict[player_id]
        
        player_color = self.get_player_color(frame, player_bbox)

        team_id = self.kmeans.predict(player_color.reshape(1, -1))[0]
        team_id += 1

        # Flip team if clusters were swapped to make Team 1 white
        if self.clusters_swapped:
            team_id = 1 if team_id == 2 else 2

        # Assign goalkeeper to the white team (Team 1)
        if player_id == 116:
            team_id = 1
            

        self.players_team_dict[player_id] = team_id

        return team_id