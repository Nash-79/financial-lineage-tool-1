# Terraform configuration for Financial Lineage Tool
# Deploys: Azure AI Foundry, Cosmos DB, AI Search, Container Apps, Storage

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.80"
    }
    azapi = {
      source  = "azure/azapi"
      version = "~> 1.10"
    }
  }
  
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfstatelineage"
    container_name       = "tfstate"
    key                  = "lineage-tool.tfstate"
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
    key_vault {
      purge_soft_delete_on_destroy = true
    }
  }
}

# Variables
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "uksouth"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "lineage"
}

locals {
  resource_prefix = "${var.project_name}-${var.environment}"
  tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "rg-${local.resource_prefix}"
  location = var.location
  tags     = local.tags
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "main" {
  name                = "law-${local.resource_prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.tags
}

# Application Insights
resource "azurerm_application_insights" "main" {
  name                = "appi-${local.resource_prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
  tags                = local.tags
}

# Key Vault
resource "azurerm_key_vault" "main" {
  name                        = "kv-${local.resource_prefix}"
  location                    = azurerm_resource_group.main.location
  resource_group_name         = azurerm_resource_group.main.name
  enabled_for_disk_encryption = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false
  sku_name                    = "standard"
  tags                        = local.tags
  
  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id
    
    key_permissions = [
      "Get", "List", "Create", "Delete", "Purge"
    ]
    
    secret_permissions = [
      "Get", "List", "Set", "Delete", "Purge"
    ]
  }
}

data "azurerm_client_config" "current" {}

# Storage Account
resource "azurerm_storage_account" "main" {
  name                     = "st${replace(local.resource_prefix, "-", "")}${random_string.storage_suffix.result}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  tags                     = local.tags
}

resource "random_string" "storage_suffix" {
  length  = 4
  special = false
  upper   = false
}

resource "azurerm_storage_container" "code_repos" {
  name                  = "code-repos"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# Azure OpenAI
resource "azurerm_cognitive_account" "openai" {
  name                = "oai-${local.resource_prefix}"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  kind                = "OpenAI"
  sku_name            = "S0"
  tags                = local.tags
  
  custom_subdomain_name = "oai-${local.resource_prefix}"
}

resource "azurerm_cognitive_deployment" "gpt4o" {
  name                 = "gpt-4o"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  
  model {
    format  = "OpenAI"
    name    = "gpt-4o"
    version = "2024-05-13"
  }
  
  scale {
    type     = "Standard"
    capacity = 30
  }
}

resource "azurerm_cognitive_deployment" "embedding" {
  name                 = "text-embedding-ada-002"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  
  model {
    format  = "OpenAI"
    name    = "text-embedding-ada-002"
    version = "2"
  }
  
  scale {
    type     = "Standard"
    capacity = 120
  }
}

# Cosmos DB (Gremlin API)
resource "azurerm_cosmosdb_account" "main" {
  name                = "cosmos-${local.resource_prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"
  tags                = local.tags
  
  capabilities {
    name = "EnableGremlin"
  }
  
  consistency_policy {
    consistency_level = "Session"
  }
  
  geo_location {
    location          = azurerm_resource_group.main.location
    failover_priority = 0
  }
}

resource "azurerm_cosmosdb_gremlin_database" "lineage" {
  name                = "lineage-db"
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
}

resource "azurerm_cosmosdb_gremlin_graph" "lineage" {
  name                = "lineage-graph"
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
  database_name       = azurerm_cosmosdb_gremlin_database.lineage.name
  partition_key_path  = "/pk"
  throughput          = 400
  
  index_policy {
    automatic      = true
    indexing_mode  = "consistent"
    included_paths = ["/*"]
  }
  
  conflict_resolution_policy {
    mode                          = "LastWriterWins"
    conflict_resolution_path      = "/_ts"
  }
}

# Azure AI Search
resource "azurerm_search_service" "main" {
  name                = "srch-${local.resource_prefix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "standard"
  replica_count       = 1
  partition_count     = 1
  tags                = local.tags
  
  semantic_search_sku = "standard"
}

# Container Registry
resource "azurerm_container_registry" "main" {
  name                = "acr${replace(local.resource_prefix, "-", "")}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Standard"
  admin_enabled       = true
  tags                = local.tags
}

# Container Apps Environment
resource "azurerm_container_app_environment" "main" {
  name                       = "cae-${local.resource_prefix}"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  tags                       = local.tags
}

# Container App - API
resource "azurerm_container_app" "api" {
  name                         = "ca-${local.resource_prefix}-api"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"
  tags                         = local.tags
  
  template {
    container {
      name   = "lineage-api"
      image  = "${azurerm_container_registry.main.login_server}/lineage-api:latest"
      cpu    = 1.0
      memory = "2Gi"
      
      env {
        name  = "AZURE_OPENAI_ENDPOINT"
        value = azurerm_cognitive_account.openai.endpoint
      }
      
      env {
        name        = "AZURE_OPENAI_API_KEY"
        secret_name = "openai-key"
      }
      
      env {
        name  = "COSMOS_ENDPOINT"
        value = "wss://${azurerm_cosmosdb_account.main.name}.gremlin.cosmos.azure.com:443/"
      }
      
      env {
        name        = "COSMOS_KEY"
        secret_name = "cosmos-key"
      }
      
      env {
        name  = "SEARCH_ENDPOINT"
        value = "https://${azurerm_search_service.main.name}.search.windows.net"
      }
      
      env {
        name        = "SEARCH_KEY"
        secret_name = "search-key"
      }
      
      liveness_probe {
        transport = "HTTP"
        path      = "/health"
        port      = 8000
      }
      
      readiness_probe {
        transport = "HTTP"
        path      = "/health"
        port      = 8000
      }
    }
    
    min_replicas = 1
    max_replicas = 5
  }
  
  secret {
    name  = "openai-key"
    value = azurerm_cognitive_account.openai.primary_access_key
  }
  
  secret {
    name  = "cosmos-key"
    value = azurerm_cosmosdb_account.main.primary_key
  }
  
  secret {
    name  = "search-key"
    value = azurerm_search_service.main.primary_key
  }
  
  ingress {
    external_enabled = true
    target_port      = 8000
    
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
  
  registry {
    server               = azurerm_container_registry.main.login_server
    username             = azurerm_container_registry.main.admin_username
    password_secret_name = "registry-password"
  }
  
  secret {
    name  = "registry-password"
    value = azurerm_container_registry.main.admin_password
  }
}

# API Management (Optional - for production)
resource "azurerm_api_management" "main" {
  count               = var.environment == "prod" ? 1 : 0
  name                = "apim-${local.resource_prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  publisher_name      = "Railpen"
  publisher_email     = "data-architecture@railpen.com"
  sku_name            = "Developer_1"
  tags                = local.tags
}

# Outputs
output "api_url" {
  description = "URL of the deployed API"
  value       = "https://${azurerm_container_app.api.ingress[0].fqdn}"
}

output "openai_endpoint" {
  description = "Azure OpenAI endpoint"
  value       = azurerm_cognitive_account.openai.endpoint
}

output "cosmos_endpoint" {
  description = "Cosmos DB Gremlin endpoint"
  value       = "wss://${azurerm_cosmosdb_account.main.name}.gremlin.cosmos.azure.com:443/"
}

output "search_endpoint" {
  description = "Azure AI Search endpoint"
  value       = "https://${azurerm_search_service.main.name}.search.windows.net"
}

output "storage_connection_string" {
  description = "Storage account connection string"
  value       = azurerm_storage_account.main.primary_connection_string
  sensitive   = true
}

output "acr_login_server" {
  description = "Container Registry login server"
  value       = azurerm_container_registry.main.login_server
}

output "app_insights_connection_string" {
  description = "Application Insights connection string"
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}
