# Script para substituir emojis por flag-icons
import re

# Ler o arquivo
with open('app/templates/auth/register.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Mapeamento de emojis para classes CSS
emoji_to_css = {
    '🇳🇱': 'fi fi-nl',
    '🇧🇪': 'fi fi-be', 
    '🇨🇭': 'fi fi-ch',
    '🇦🇹': 'fi fi-at',
    '🇩🇰': 'fi fi-dk',
    '🇸🇪': 'fi fi-se',
    '🇳🇴': 'fi fi-no',
    '🇫🇮': 'fi fi-fi',
    '🇵🇱': 'fi fi-pl',
    '🇦🇷': 'fi fi-ar',
    '🇨🇱': 'fi fi-cl',
    '🇨🇴': 'fi fi-co',
    '🇵🇪': 'fi fi-pe',
    '🇲🇽': 'fi fi-mx'
}

# Substituir os emojis no data-flag
for emoji, css_class in emoji_to_css.items():
    content = content.replace(f'data-flag="{emoji}"', f'data-flag="{css_class}"')

# Substituir os spans com emojis por spans com classes CSS
for emoji, css_class in emoji_to_css.items():
    content = content.replace(
        f'<span class="mr-3 text-lg">{emoji}</span>',
        f'<span class="{css_class} mr-3" style="width: 24px; height: 18px;"></span>'
    )

# Gravar o arquivo
with open('app/templates/auth/register.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Substituição de emojis por flag-icons concluída!")
