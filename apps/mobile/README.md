# 🐝 BeeSpace Mobile

> Aplicativo mobile do BeeSpace para manejo presencial, telemetria IoT, visão computacional e alertas ambientais com Copernicus.

## => Objetivo

[ Mobile ] Interface de campo para o produtor acompanhar a colmeia inteligente.  
[ Manejo ] Base para registrar fotos dos quadros e acionar inferência YOLO.  
[ Telemetria ] Visualização de temperatura, umidade, peso, bateria, fluxo de abelhas e estresse acústico.  
[ Copernicus ] Exibição de alertas cruzando colmeia, Sentinel-2, HR-VPP, Sentinel-5P/CAMS e C3S/ERA5.

## => Stack

# Expo + React Native  
# TypeScript estrito  
# Componentes reutilizáveis  
# Serviço mockável preparado para troca por API real

## => Estrutura

```text
apps/mobile/
├── App.tsx
├── README.md
├── app.json
├── babel.config.js
├── package.json
├── tsconfig.json
└── src/
    ├── components/
    ├── data/
    ├── services/
    ├── theme.ts
    ├── types/
    └── utils/
```

## => Como executar

```bash
cd apps/mobile
npm install
npm run start
```

## => Próximas integrações

# Substituir `src/services/api.ts` por cliente HTTP da API BeeSpace.  
# Conectar câmera/galeria para envio de fotos ao pipeline YOLO.  
# Adicionar autenticação de produtores e propriedades.  
# Persistir histórico offline para manejo em áreas sem conectividade.  
# Integrar notificações push para alertas críticos de biodiversidade.
