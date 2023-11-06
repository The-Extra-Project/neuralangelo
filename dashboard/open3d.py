import open3d


if __name__ == "__main__":
    pcd = open3d.io.read_point_cloud("../datasets/tanks_and_temples/Barn/Barn.ply")
    open3d.visualization.draw_geometries([pcd], zoom=0.123,front=[0.4257, -0.2125, -0.8795], lookat=[2.6172, 2.0475, 1.532],up=[-0.0694, -0.9768, 0.2024])
    