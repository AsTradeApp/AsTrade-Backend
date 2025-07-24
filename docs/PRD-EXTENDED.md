PRD técnico para implementar **la habilitación completa de un usuario de la aplicación de AsTrade para la API de Extended**. Seguimiento paso a paso.

El objetivo es que el usuario final pueda operar órdenes reales en la red **Testnet** y **Mainnet** de Extended.

---

1. Recibir datos de autenticación (Google/Apple) del frontend y asociarlos a una wallet de Starknet.
2. Crear una cuenta de Extended con la wallet de Starknet.
3. Configurar Testnet/Mainnet según el nivel del usuario.
4. Autenticar solicitudes con API Key y firmas Stark.
5. Permitir creación de hasta 10 subcuentas de Extended.
6. Permitir trading simulado (Testnet) y real (Mainnet).
7. Monitorear órdenes con WebSocket.
8. Manejar errores básicos (ej. clave inválida).
9. Almacenar claves de forma segura.

A TENER EN CUENTA:

**Credenciales**
   - [ ] Cuenta en Extended creada por Usuario
   - [ ] API Key y Secret generadas
   - [ ] Extended Stark private key generada
   - [ ] Public Key derivada y asociada en plataforma

**Entorno local**
   - [ ] Interacción con los endpoints y posibilidades que propone Extended
   - [ ] Variables de entorno configuradas y manejadas de manera cuidadosa como veniamos planteando(el manejo cuidadoso de la extended_stark_private_key)

   **Autenticación**
   - [ ] Cliente autenticado correctamente
   - [ ] Endpoint privado verificado (e.g. balances)

   **Preparación del mercado**
   - [ ] Instrumentos disponibles consultados
   - [ ] BTC-PERP confirmado activo
   - [ ] Parámetros de trading conocidos

   **Trading (para testear la integración)**
   - [ ] Orden de compra de 0.1 BTC-PERP enviada en Testnet
   - [ ] ID de orden recibido

   **Seguimiento**
   - [ ] WebSocket conectado
   - [ ] Estado de la orden recibido y procesado (hago un parentésis en esta parte ya que quiero usar websocket porque considero que puede ser útil para el trading real)

   **Post-operación**
   - [ ] Balance actualizado consultado
   - [ ] Historial de órdenes/fills probado
   - [ ] Flujo completo de trading validado