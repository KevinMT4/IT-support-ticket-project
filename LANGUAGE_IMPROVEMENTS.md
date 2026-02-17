# Mejoras en el Sistema de Idiomas - TicketsCofat

## Descripción General

Se ha mejorado significativamente el sistema de cambio de idioma de la aplicación para proporcionar una experiencia más completa y robusta en toda la interfaz.

## Cambios Implementados

### 1. Configuración Mejorada de i18n (`src/i18n.js`)

- **Detección automática del idioma del navegador**: Ahora la aplicación detecta el idioma preferido del usuario basándose en:
    - Preferencia guardada en localStorage
    - Idioma del navegador (`navigator.language`)
    - Fallback a español por defecto
- **Actualización del atributo `lang` del HTML**: Se actualiza automáticamente para mejorar la accesibilidad y SEO
- **Manejo de RTL**: Preparado para soportar idiomas de derecha a izquierda en el futuro
- **Suspense deshabilitado**: `useSuspense: false` para mejor manejo de componentes

### 2. Hook Personalizado `useLanguage` (`src/hooks/useLanguage.js`)

Nuevo hook que centraliza toda la lógica de idioma:

```javascript
const {
    currentLanguage, // Idioma actual
    changeLanguage, // Cambiar idioma
    isLanguage, // Verificar si es un idioma específico
    t, // Función de traducción
    i18n, // Objeto i18n completo
    getLanguageName, // Obtener nombre del idioma
} = useLanguage();
```

**Ventajas:**

- Centraliza la lógica de cambio de idioma
- Proporciona funciones útiles para trabajar con idiomas
- Facilita tests unitarios
- Mejor mantenibilidad

### 3. LanguageSwitcher Mejorado (`src/components/LanguageSwitcher.jsx`)

```jsx
// Antes: Simple con texto "ES" / "EN"
// Ahora: Incluye emojis de banderas y mejore UX
```

**Mejoras:**

- Emojis de banderas (🇪🇸 y 🇬🇧)
- Atributos ARIA para accesibilidad
- `aria-pressed` para indicar idioma activo
- Animaciones suaves (escalado al hover)
- Visual mejorado con iconos

### 4. Traducciones Completas

Se agregaron nuevas traducciones faltantes:

**Español:**

- `messages.stateUpdatedSuccessfully`: "Estado actualizado correctamente"
- `messages.priorityUpdatedSuccessfully`: "Prioridad actualizada correctamente"
- `messages.errorUpdatingStatus`: "Error al actualizar el estado"
- `messages.errorUpdatingPriority`: "Error al actualizar la prioridad"
- `messages.close`: "Cerrar"
- `ticketDetail.errorLoadingTicket`: "Error al cargar el ticket"
- `ticketDetail.noAvailableActions`: "No hay acciones disponibles"

**English:**

- `messages.stateUpdatedSuccessfully`: "Status updated successfully"
- `messages.priorityUpdatedSuccessfully`: "Priority updated successfully"
- `messages.errorUpdatingStatus`: "Error updating status"
- `messages.errorUpdatingPriority`: "Error updating priority"
- `messages.close`: "Close"
- `ticketDetail.errorLoadingTicket`: "Error loading ticket"
- `ticketDetail.noAvailableActions`: "No available actions"

### 5. Eliminación de Strings Hard-Coded

Se reemplazaron todos los textos hard-coded con traducciones:

**Componentes actualizados:**

- `Toast.jsx`: Ahora usa `t('messages.close')`
- `Alert.jsx`: Ahora usa `t('messages.close')`
- `ConfirmModal.jsx`: Usa `t('form.cancel')` y `t('form.confirm')`
- `TicketDetail.jsx`: Todas las traducciones ahora son dinámicas
- `Layout.jsx`: Mejorado con ARIA labels traducidos

### 6. Mejoras de Accesibilidad

Se agregaron atributos ARIA en toda la aplicación:

```jsx
// LanguageSwitcher
<div role="group" aria-label="Language selector">
  <button aria-pressed={currentLanguage === lang.code} />
</div>

// ConfirmModal
<div role="dialog" aria-modal="true" aria-labelledby="modal-title">

// Alert
<div role="alert">

// Toast
<div role="alert" aria-live="polite">

// Layout
<nav role="navigation" aria-label="Main navigation">
<main role="main">
```

### 7. Estilos Mejorados (`src/styles/LanguageSwitcher.css`)

```css
/* Añadido */
- Icono de globo terráqueo
- Animaciones de transición suave
- Escalado en hover (transform: scale(1.05))
- Shadow en estado activo
- Layout responsive mejorado
- Separación clara de banderas y códigos
```

**Responsive:**

- Desktop: Muestra icono + banderas + códigos
- Mobile: Solo muestra banderas

### 8. Actualización de package.json

Se agregó librería para detección de idioma:

```json
"i18next-browser-languagedetector": "^8.0.0"
```

**Nota:** Esta librería está importada en i18n.js pero puede ser utilizada directamente si se necesita más controlode la detección.

## Paginas Actualizadas

- `pages/Login.jsx` → Usa `useLanguage()`
- `pages/TicketsList.jsx` → Usa `useLanguage()`
- `pages/CreateTicket.jsx` → Usa `useLanguage()`
- `pages/TicketDetail.jsx` → Usa `useLanguage()` y formato de fecha dinámico

## Flujo de Cambio de Idioma

```
Usuario hace clic en botón de idioma
    ↓
handleLanguageChange(lang)
    ↓
changeLanguage(lang) en hook
    ↓
i18n.changeLanguage(lang)
    ↓
localStorage.setItem("language", lang)
    ↓
document.documentElement.lang = lang (automático)
    ↓
Todos los componentes se re-renderean con nuevas traducciones
    ↓
Persistencia: Próxima visita carga el idioma guardado
```

## Beneficios

✅ **Mejor experiencia de usuario**

- Detección automática del idioma preferido
- Persistencia del idioma entre sesiones
- Cambio de idioma instantáneo
- Visual más atractivo

✅ **Mejor accesibilidad**

- Atributos ARIA completos
- Atributo `lang` actualizado automáticamente
- Labels traducidos para screen readers
- Indicadores visuales de estado activo

✅ **Mejor mantenibilidad**

- Hook centralizado `useLanguage()`
- Punto único de cambio de idioma
- Fácil de probar unitariamente
- Código más limpio y consistente

✅ **Mejor escalabilidad**

- Preparado para agregar más idiomas
- Estructura de traducciones extensible
- Fácil de integrar con backends
- Soporte para formatos de fecha localizados

## Próximas Mejoras Sugeridas

1. **Testing**: Agregar pruebas unitarias para el hook `useLanguage`
2. **Backend**: Guardar preferencia de idioma en BD del usuario
3. **Más idiomas**: Agregar portuguès, francés, etc.
4. **Lazy loading**: Cargar traducciones bajo demanda
5. **Pluralizacion**: Agregar soporte para plurales
6. **Namespace**: Organizar traducciones en namespaces si crecen

## Instalación de Dependencias

```bash
cd client
npm install
```

Se instalará automáticamente:

- `i18next`
- `react-i18next`
- `i18next-browser-languagedetector` (NEW)

## Uso del Hook

```javascript
import { useLanguage } from "../hooks/useLanguage";

function MyComponent() {
    const { t, currentLanguage, changeLanguage } = useLanguage();

    return (
        <div>
            <p>{t("common.myTickets")}</p>
            <button onClick={() => changeLanguage("es")}>Español</button>
            <p>Idioma actual: {currentLanguage}</p>
        </div>
    );
}
```

## Soporte Técnico

Si tienes preguntas sobre la implementación, revisa:

- `src/hooks/useLanguage.js` - Hook centralizado
- `src/i18n.js` - Configuración principal
- `src/locales/*.json` - Archivos de traducción
