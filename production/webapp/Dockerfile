# Étape 1 : Construire l'application avec Node.js
FROM node:latest AS build

# Définir le dossier de travail pour la compilation
WORKDIR /build

# Copier les fichiers de configuration npm pour installer les dépendances
COPY package.json package-lock.json ./

# Installer uniquement les dépendances nécessaires
RUN npm ci

# Copier le reste des fichiers de l'application
COPY public/ public
COPY src/ src
COPY index.html index.html
COPY vite.config.js vite.config.js

# Exécuter la commande de build pour générer les fichiers de production
RUN npm run build

# Étape 2 : Préparer l'image de production avec nginx
FROM nginx:alpine

# Copier les fichiers build depuis l'étape précédente
COPY --from=build /build/dist/ /usr/share/nginx/html

# Créer les répertoires requis et définir les permissions
RUN mkdir -p /var/cache/nginx/client_temp && \
    chown -R 1001:1001 /var/cache/nginx

# Créer un utilisateur non-root pour exécuter nginx
RUN adduser -D -H -u 1001 appuser

# Utiliser cet utilisateur pour exécuter le serveur Nginx
USER appuser

# Exposer le port 80
EXPOSE 80

# Démarrer nginx en tant qu'utilisateur non-root
CMD ["nginx", "-g", "daemon off;"]
