resource "docker_image" "backend_image" {
  name = "backend-image:latest"
  build {
    context = "${path.root}/../macroeconomics_simulator"
    dockerfile = "Dockerfile"
    tag = ["backend-image:latest"]
  }
}

resource "docker_image" "frontend_image" {
  name = "frontend-image:latest"
  build {
    context = "${path.root}/../frontend"
    dockerfile = "Dockerfile"
    tag = ["frontend-image:latest"]
  }
}

output "backend_image" {
  value = docker_image.backend_image.name
}

output "frontend_image" {
  value = docker_image.frontend_image.name
}