/**
 * Font Loader - Carrega fontes web de forma otimizada
 * Substitui o onload inline por um método mais seguro compatível com CSP
 */
document.addEventListener('DOMContentLoaded', function() {
    // Encontra links de fontes com media="print"
    const fontLinks = document.querySelectorAll('link[rel="stylesheet"][media="print"]');
    
    // Altera o media para "all" para carregar as fontes
    fontLinks.forEach(link => {
        link.media = 'all';
    });
    
    console.log('🔤 Fontes carregadas com sucesso');
});
