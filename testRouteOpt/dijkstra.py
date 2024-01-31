import heapq

def dijkstra(graph, start):
    # Initialize distances and predecessors
    distances = {vertex: float('infinity') for vertex in graph}
    distances[start] = 0
    predecessors = {vertex: None for vertex in graph}
    
    # Priority queue to store vertices with their distances
    priority_queue = [(0, start)]
    
    while priority_queue:
        current_distance, current_vertex = heapq.heappop(priority_queue)
        
        # Check if the current distance is already greater than the stored distance
        if current_distance > distances[current_vertex]:
            continue
        
        for neighbor, weight in graph[current_vertex].items():
            distance = current_distance + weight
            
            # Relaxation step
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_vertex
                heapq.heappush(priority_queue, (distance, neighbor))
    
    return distances, predecessors

# Example usage:
graph = {
    'A': {'B': 1, 'D': 3},
    'B': {'A': 1, 'C': 1, 'D': 4},
    'C': {'B': 1, 'D': 1},
    'D': {'A': 3, 'B': 4, 'C': 1}
}

start_vertex = 'A'
distances, predecessors = dijkstra(graph, start_vertex)

# Print shortest distances and paths
for vertex, distance in distances.items():
    path = []
    current_vertex = vertex
    while current_vertex is not None:
        path.insert(0, current_vertex)
        current_vertex = predecessors[current_vertex]
    print(f"Shortest path from {start_vertex} to {vertex}: {path} with distance {distance}")
