INSTRUCCIONES PARA EL DESARROLLO

 - Hacer bun i 
 para instalar los paquetes necesarios para el correcto desarrollo de la aplicación



INSTRUCCIONES DE DESPLIEGUE EN RAILWAY

Este documento contiene los pasos necesarios para desplegar la aplicación en Railway y gestionar el repositorio correctamente.

PREPARACIÓN DEL REPOSITORIO

1. Verificar el archivo .gitignore:
   - Asegúrate de que la línea "# dist/" esté comentada en el archivo .gitignore. Esto permite que la carpeta "dist/" se incluya temporalmente para el despliegue en Railway.
   - Ejemplo:
     Antes: # dist/
     Después: dist/

DESPLIEGUE EN RAILWAY

1. Iniciar Sesión en Railway:
   - Verifica que estés logueado en la CLI de Railway. Si no lo estás, ejecuta:
     railway login

2. Linkear el Proyecto:
   - Conecta tu proyecto local con el proyecto en Railway usando:
     railway link
   - Sigue las instrucciones para seleccionar el proyecto correcto.

3. Desplegar la Aplicación:
   - Una vez linkeado, despliega la aplicación con:
     railway up
   - Esto subirá el código y desplegará la aplicación en Railway.

POST-DESPLIEGUE Y GESTIÓN DEL REPOSITORIO

1. Restaurar el .gitignore:
   - Después de desplegar, descomenta la línea "# dist/" en el .gitignore para evitar subir la carpeta "dist/" al repositorio en futuros commits.
   - Ejemplo:
     Antes: dist/
     Después: # dist/

2. Hacer Push al Repositorio:
   - Con "# dist/" comentado, haz push de tus cambios al repositorio remoto sin incluir el build:
     git add .
     git commit -m "Actualización post-despliegue"
     git push origin main

NOTAS ADICIONALES
- Asegúrate de tener instalada la CLI de Railway antes de comenzar. Puedes instalarla con:
  npm install -g @railway/cli
- Si tu proyecto requiere un build previo (por ejemplo, "npm run build"), ejecuta ese comando antes de hacer "railway up" para generar la carpeta "dist/".

¡Listo! Tu aplicación debería estar desplegada en Railway y tu repositorio gestionado correctamente.