"""
Extended SDK Configuration Adapter
"""
from dataclasses import dataclass
from typing import Optional, Dict
from app.config.extended_config import extended_config


@dataclass
class ExtendedEndpointConfig:
    """
    Configuration adapter for x10.perpetual SDK EndpointConfig
    Bridges our app configuration with the SDK requirements
    """
    base_url: str
    onboarding_url: str
    signing_domain: str
    ws_url: str
    
    @property
    def api_base_url(self) -> str:
        """
        Property required by X10 SDK
        Returns the base URL for API endpoints
        """
        return self.base_url

    @property
    def stream_url(self) -> str:
        """
        Property required by X10 SDK
        Returns the WebSocket stream URL
        """
        return self.ws_url
    
    @property
    def headers(self) -> Dict[str, str]:
        """
        Property required by X10 SDK
        Returns the headers for API requests
        """
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "AsTrade/1.0.0 (compatible; MyApp/1.0; +https://extended.exchange)",
            "X-Api-Key": extended_config.headers.get("X-Api-Key", "")
        }
    
    @property
    def ws_headers(self) -> Dict[str, str]:
        """
        Property for WebSocket connection headers
        """
        return {
            "User-Agent": "AsTrade/1.0.0 (compatible; MyApp/1.0; +https://extended.exchange)",
            "X-Api-Key": extended_config.headers.get("X-Api-Key", "")
        }
    
    @classmethod
    def from_environment(cls, environment: str = "testnet") -> "ExtendedEndpointConfig":
        """
        Create configuration from environment setting
        
        Args:
            environment: "testnet" or "mainnet"
            
        Returns:
            ExtendedEndpointConfig instance
        """
        if environment == "mainnet":
            return cls(
                base_url=extended_config.MAINNET_BASE_URL,
                onboarding_url=extended_config.MAINNET_ONBOARDING_URL,
                signing_domain=extended_config.MAINNET_SIGNING_DOMAIN,
                ws_url=extended_config.MAINNET_WS_URL
            )
        else:
            return cls(
                base_url=extended_config.TESTNET_BASE_URL,
                onboarding_url=extended_config.TESTNET_ONBOARDING_URL,
                signing_domain=extended_config.TESTNET_SIGNING_DOMAIN_NEW,
                ws_url=extended_config.TESTNET_WS_URL
            )
    
    @classmethod
    def get_current(cls) -> "ExtendedEndpointConfig":
        """Get configuration for current environment"""
        return cls(
            base_url=extended_config.base_url,
            onboarding_url=extended_config.onboarding_url,
            signing_domain=extended_config.signing_domain,
            ws_url=extended_config.ws_url
        )


# Create TESTNET and MAINNET config instances compatible with SDK
TESTNET_CONFIG = ExtendedEndpointConfig.from_environment("testnet")
MAINNET_CONFIG = ExtendedEndpointConfig.from_environment("mainnet") 