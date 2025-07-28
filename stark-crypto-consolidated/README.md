# StarkNet Crypto Wrapper - Consolidated

Esta carpeta contiene todos los archivos necesarios para el wrapper de criptografía StarkNet, consolidados desde los repositorios externos para uso independiente en AsTrade backend.

## 📁 Estructura

```
stark-crypto-consolidated/
├── src/                    # Código fuente del wrapper Python-Rust
├── rust-crypto-lib-base/   # Biblioteca base de criptografía StarkNet
│   ├── src/
│   │   ├── lib.rs
│   │   └── starknet_messages.rs
│   └── Cargo.toml
├── python/                 # Módulo Python compilado
│   └── fast_stark_crypto/
├── Cargo.toml             # Configuración principal de Rust
├── pyproject.toml         # Configuración de Python
└── Cargo.lock             # Dependencias bloqueadas
```

## 🚀 Uso

### Construir el wrapper

```bash
cd stark-crypto-consolidated
maturin develop
```

### Usar en Python

```python
import fast_stark_crypto

# Generar clave pública
private_key = 0x1234567890abcdef...
public_key = fast_stark_crypto.get_public_key(private_key)

# Firmar mensaje
message = "Hello StarkNet"
signature = fast_stark_crypto.sign(message, private_key)

# Verificar firma
is_valid = fast_stark_crypto.verify(message, signature, public_key)

# Calcular hash de orden para Extended Exchange
order_hash = fast_stark_crypto.get_order_msg_hash(
    position_id=0,
    base_asset_id=123,
    base_amount=500000,
    quote_asset_id=456,
    quote_amount=1000000,
    fee_asset_id=789,
    fee_amount=1000,
    expiration=1234567890,
    salt=123456789,
    user_public_key=public_key,
    domain_name="extended.exchange",
    domain_version="1",
    domain_chain_id="1",
    domain_revision="1"
)
```

## 🔧 Funciones Disponibles

- `get_public_key(private_key: int) -> str`
- `sign(message: str, private_key: int) -> str`
- `verify(message: str, signature: str, public_key: str) -> bool`
- `pedersen_hash(a: str, b: str) -> str`
- `get_order_msg_hash(...) -> str`
- `get_transfer_msg_hash(...) -> str`

## 📦 Dependencias

- Rust 1.70+
- maturin
- pyo3
- starknet-crypto

## 🎯 Propósito

Este wrapper permite usar wallets StarkNet nativas (Argent, Braavos) para crear cuentas en Extended Exchange y firmar órdenes sin depender de Ethereum. 