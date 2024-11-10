resource "docker_image" "backend_image" {
  name = "backend-image"
  build {
    context = "${path.root}/../macroeconomics_simulator"
    dockerfile = "Dockerfile"
    tag = ["backend-image:latest"]
  }
}

resource "docker_image" "frontend_image" {
  name = "frontend-image"
  build {
    context = "${path.root}/../frontend"
    dockerfile = "Dockerfile"
    tag = ["frontend-image:latest"]
  }
}

output "backend_image_latest" {
  value = docker_image.backend_image.name
}

output "frontend_image_latest" {
  value = docker_image.frontend_image.name
}