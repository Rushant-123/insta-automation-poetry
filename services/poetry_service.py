import random
import asyncio
import logging
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime
import httpx

from .poetry_scraper import PoetryScraper
from .poetry_models import Poetry
from config.settings import settings

logger = logging.getLogger(__name__)

# Try to import OpenAI, handle if not available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available. Install with: pip install openai")


class PoetryService:
    """Service for curating and managing poetry content."""
    
    def __init__(self):
        """Initialize poetry service."""
        self.poetry_database: List[Poetry] = []
        self.cache_file = "assets/poetry_cache.json"
        
        # Azure OpenAI GPT configuration
        base_endpoint = settings.azure_openai_endpoint.rstrip('/')  # Remove trailing slash if present
        self.gpt_endpoint = f"{base_endpoint}/openai/deployments/{settings.azure_openai_deployment_name}/chat/completions?api-version={settings.azure_openai_api_version}"
        self.gpt_api_key = settings.azure_openai_api_key
        self.gpt_deployment = settings.azure_openai_deployment_name
        self.gpt_api_version = settings.azure_openai_api_version
        
        # Famous poets for style reference
        self.famous_poets = [
            {"name": "Robert Frost", "style": "nature-focused, contemplative"},
            {"name": "Emily Dickinson", "style": "introspective, metaphysical"},
            {"name": "Maya Angelou", "style": "powerful, uplifting"},
            {"name": "Langston Hughes", "style": "rhythmic, soulful"},
            {"name": "Mary Oliver", "style": "nature-observant, mindful"},
            {"name": "Rumi", "style": "spiritual, mystical"},
            {"name": "William Wordsworth", "style": "romantic, naturalistic"},
            {"name": "Walt Whitman", "style": "expansive, celebratory"}
        ]
        
    async def initialize(self):
        """Initialize poetry database (no cache, only built-in)."""
        logger.info("Initializing poetry database...")
        await self._add_builtin_poetry()

    async def _load_cached_poetry(self):
        """Load poetry from cache file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    poems_data = json.load(f)
                    self.poetry_database = [
                        Poetry(**poem_dict) for poem_dict in poems_data
                    ]
                logger.info(f"Loaded {len(self.poetry_database)} poems from cache")
        except Exception as e:
            logger.error(f"Failed to load poetry cache: {e}")
            
    async def _save_poetry_cache(self):
        """Save poetry to cache file."""
        try:
            poems_data = [
                {
                    "lines": poem.lines,
                    "author": poem.author,
                    "title": poem.title,
                    "source": poem.source,
                    "theme": poem.theme,
                    "created_at": poem.created_at.isoformat() if poem.created_at else None
                }
                for poem in self.poetry_database
            ]
            
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(poems_data, f, indent=2)
            logger.info(f"Saved {len(poems_data)} poems to cache")
        except Exception as e:
            logger.error(f"Failed to save poetry cache: {e}")
            
    async def _fetch_initial_poetry(self):
        """Fetch initial poetry from various sources."""
        logger.info("Fetching initial poetry collection...")
        
        # Add built-in poetry collection
        await self._add_builtin_poetry()
        
        # Attempt to fetch from online sources using scraper
        try:
            await self._fetch_from_scraper()
        except Exception as e:
            logger.warning(f"Failed to fetch from scraper: {e}")
            
        # Keep the old method calls for backwards compatibility
        try:
            await self._fetch_poetry_foundation()
        except Exception as e:
            logger.warning(f"Failed to fetch from Poetry Foundation: {e}")
            
        try:
            await self._fetch_public_domain_poetry()
        except Exception as e:
            logger.warning(f"Failed to fetch public domain poetry: {e}")
            
    async def _fetch_from_scraper(self):
        """Fetch poetry using the poetry scraper."""
        try:
            from services.poetry_scraper import PoetryScraper
            
            async with PoetryScraper() as scraper:
                # Fetch a smaller number initially to avoid overloading
                scraped_poems = await scraper.scrape_all_sources(poems_per_source=5)
                
                if scraped_poems:
                    self.poetry_database.extend(scraped_poems)
                    logger.info(f"Added {len(scraped_poems)} scraped poems")
                    
        except Exception as e:
            logger.error(f"Failed to fetch poetry from scraper: {e}")
            
    async def _add_builtin_poetry(self):
        """Add built-in poetry collection for reliable fallback."""
        builtin_poems = [
            # Robert Frost
            Poetry(
                lines=[
                    "Two roads diverged in a yellow wood,",
                    "And sorry I could not travel both",
                    "And be one traveler, long I stood",
                    "And looked down one as far as I could"
                ],
                author="Robert Frost",
                title="The Road Not Taken",
                source="builtin"
            ),
            Poetry(
                lines=[
                    "The woods are lovely, dark and deep,",
                    "But I have promises to keep,",
                    "And miles to go before I sleep,",
                    "And miles to go before I sleep."
                ],
                author="Robert Frost",
                title="Stopping by Woods on a Snowy Evening",
                source="builtin"
            ),
            Poetry(
                lines=[
                    "Something there is that doesn't love a wall,",
                    "That sends the frozen-ground-swell under it,",
                    "And spills the upper boulders in the sun;",
                    "And makes gaps even two can pass abreast."
                ],
                author="Robert Frost",
                title="Mending Wall",
                source="builtin"
            ),
            Poetry(
                lines=[
                    "I took the one less traveled by,",
                    "And that has made all the difference.",
                    "Yet knowing how way leads on to way,",
                    "I doubted if I should ever come back."
                ],
                author="Robert Frost",
                title="The Road Not Taken (excerpt)",
                source="builtin"
            ),
            
            # William Wordsworth
            Poetry(
                lines=[
                    "I wandered lonely as a cloud",
                    "That floats on high o'er vales and hills,",
                    "When all at once I saw a crowd,",
                    "A host of golden daffodils."
                ],
                author="William Wordsworth",
                title="Daffodils",
                source="builtin"
            ),
            Poetry(
                lines=[
                    "The child is father of the man;",
                    "And I could wish my days to be",
                    "Bound each to each by natural piety.",
                    "My heart leaps up when I behold"
                ],
                author="William Wordsworth",
                title="My Heart Leaps Up",
                source="builtin"
            ),
            
            # Emily Dickinson
            Poetry(
                lines=[
                    "Hope is the thing with feathers",
                    "That perches in the soul,",
                    "And sings the tune without the words,",
                    "And never stops at all."
                ],
                author="Emily Dickinson",
                title="Hope",
                source="builtin"
            ),
            Poetry(
                lines=[
                    "I'm nobody! Who are you?",
                    "Are you nobody, too?",
                    "Then there's a pair of us - don't tell!",
                    "They'd banish us, you know."
                ],
                author="Emily Dickinson",
                title="I'm Nobody",
                source="builtin"
            ),
            Poetry(
                lines=[
                    "Because I could not stop for Death,",
                    "He kindly stopped for me;",
                    "The carriage held but just ourselves",
                    "And Immortality."
                ],
                author="Emily Dickinson",
                title="Because I Could Not Stop for Death",
                source="builtin"
            ),
            
            # Maya Angelou
            Poetry(
                lines=[
                    "Out of the huts of history's shame",
                    "I rise",
                    "Up from a past that's rooted in pain",
                    "I rise"
                ],
                author="Maya Angelou",
                title="Still I Rise",
                source="builtin"
            ),
            Poetry(
                lines=[
                    "You may write me down in history",
                    "With your bitter, twisted lies,",
                    "You may trod me in the very dirt",
                    "But still, like dust, I'll rise."
                ],
                author="Maya Angelou",
                title="Still I Rise (excerpt)",
                source="builtin"
            ),
            
            # Langston Hughes
            Poetry(
                lines=[
                    "Hold fast to dreams",
                    "For if dreams die",
                    "Life is a broken-winged bird",
                    "That cannot fly."
                ],
                author="Langston Hughes",
                title="Dreams",
                source="builtin"
            ),
            Poetry(
                lines=[
                    "What happens to a dream deferred?",
                    "Does it dry up",
                    "like a raisin in the sun?",
                    "Or fester like a sore—"
                ],
                author="Langston Hughes",
                title="Harlem",
                source="builtin"
            ),
            Poetry(
                lines=[
                    "I've known rivers:",
                    "I've known rivers ancient as the world and older than the",
                    "flow of human blood in human veins.",
                    "My soul has grown deep like the rivers."
                ],
                author="Langston Hughes",
                title="The Negro Speaks of Rivers",
                source="builtin"
            ),
            
            # Walt Whitman
            Poetry(
                lines=[
                    "I celebrate myself, and sing myself,",
                    "And what I assume you shall assume,",
                    "For every atom belonging to me as good belongs to you.",
                    "I loafe and invite my soul,"
                ],
                author="Walt Whitman",
                title="Song of Myself",
                source="builtin"
            ),
            Poetry(
                lines=[
                    "O Captain! My Captain! our fearful trip is done,",
                    "The ship has weather'd every rack, the prize we sought is won,",
                    "The port is near, the bells I hear, the people all exulting,",
                    "While follow eyes the steady keel, the vessel grim and daring;"
                ],
                author="Walt Whitman",
                title="O Captain! My Captain!",
                source="builtin"
            ),
            
            # William Shakespeare
            Poetry(
                lines=[
                    "Shall I compare thee to a summer's day?",
                    "Thou art more lovely and more temperate:",
                    "Rough winds do shake the darling buds of May,",
                    "And summer's lease hath all too short a date:"
                ],
                author="William Shakespeare",
                title="Sonnet 18",
                source="builtin"
            ),
            Poetry(
                lines=[
                    "To be, or not to be, that is the question:",
                    "Whether 'tis nobler in the mind to suffer",
                    "The slings and arrows of outrageous fortune,",
                    "Or to take arms against a sea of troubles"
                ],
                author="William Shakespeare",
                title="Hamlet",
                source="builtin"
            ),
            
            # Edgar Allan Poe
            Poetry(
                lines=[
                    "Once upon a midnight dreary, while I pondered, weak and weary,",
                    "Over many a quaint and curious volume of forgotten lore—",
                    "While I nodded, nearly napping, suddenly there came a tapping,",
                    "As of some one gently rapping, rapping at my chamber door."
                ],
                author="Edgar Allan Poe",
                title="The Raven",
                source="builtin"
            ),
            Poetry(
                lines=[
                    "It was many and many a year ago,",
                    "In a kingdom by the sea,",
                    "That a maiden there lived whom you may know",
                    "By the name of Annabel Lee;"
                ],
                author="Edgar Allan Poe",
                title="Annabel Lee",
                source="builtin"
            ),
            
            # Rudyard Kipling
            Poetry(
                lines=[
                    "If you can keep your head when all about you",
                    "Are losing theirs and blaming it on you,",
                    "If you can trust yourself when all men doubt you,",
                    "But make allowance for their doubting too;"
                ],
                author="Rudyard Kipling",
                title="If",
                source="builtin"
            ),
            
            # Lord Byron
            Poetry(
                lines=[
                    "She walks in beauty, like the night",
                    "Of cloudless climes and starry skies;",
                    "And all that's best of dark and bright",
                    "Meet in her aspect and her eyes:"
                ],
                author="Lord Byron",
                title="She Walks in Beauty",
                source="builtin"
            ),
            
            # Percy Bysshe Shelley
            Poetry(
                lines=[
                    "I met a traveller from an antique land,",
                    "Who said—Two vast and trunkless legs of stone",
                    "Stand in the desert. Near them, on the sand,",
                    "Half sunk a shattered visage lies, whose frown,"
                ],
                author="Percy Bysshe Shelley",
                title="Ozymandias",
                source="builtin"
            ),
            
            # John Keats
            Poetry(
                lines=[
                    "A thing of beauty is a joy for ever:",
                    "Its loveliness increases; it will never",
                    "Pass into nothingness; but still will keep",
                    "A bower quiet for us, and a sleep"
                ],
                author="John Keats",
                title="Endymion",
                source="builtin"
            ),
            Poetry(
                lines=[
                    "Season of mists and mellow fruitfulness,",
                    "Close bosom-friend of the maturing sun;",
                    "Conspiring with him how to load and bless",
                    "With fruit the vines that round the thatch-eves run;"
                ],
                author="John Keats",
                title="To Autumn",
                source="builtin"
            ),
            
            # William Blake
            Poetry(
                lines=[
                    "Tyger Tyger, burning bright,",
                    "In the forests of the night;",
                    "What immortal hand or eye,",
                    "Could frame thy fearful symmetry?"
                ],
                author="William Blake",
                title="The Tyger",
                source="builtin"
            ),
            Poetry(
                lines=[
                    "Little Lamb who made thee",
                    "Dost thou know who made thee",
                    "Gave thee life & bid thee feed.",
                    "By the stream & o'er the mead;"
                ],
                author="William Blake",
                title="The Lamb",
                source="builtin"
            ),
            
            # Alfred Lord Tennyson
            Poetry(
                lines=[
                    "'Tis better to have loved and lost",
                    "Than never to have loved at all.",
                    "Strong Son of God, immortal Love,",
                    "Whom we, that have not seen thy face,"
                ],
                author="Alfred Lord Tennyson",
                title="In Memoriam A.H.H.",
                source="builtin"
            ),
            Poetry(
                lines=[
                    "Half a league, half a league,",
                    "Half a league onward,",
                    "All in the valley of Death",
                    "Rode the six hundred."
                ],
                author="Alfred Lord Tennyson",
                title="The Charge of the Light Brigade",
                source="builtin"
            ),
            
            # Ralph Waldo Emerson
            Poetry(
                lines=[
                    "What is success?",
                    "To laugh often and much;",
                    "To win the respect of intelligent people",
                    "and the affection of children;"
                ],
                author="Ralph Waldo Emerson",
                title="Success",
                source="builtin"
            ),
            
            # Henry David Thoreau
            Poetry(
                lines=[
                    "I went to the woods to live deliberately,",
                    "To front only the essential facts of life,",
                    "And see if I could not learn what it had to teach,",
                    "And not, when I came to die, discover that I had not lived."
                ],
                author="Henry David Thoreau",
                title="Walden",
                source="builtin"
            ),
            
            # Carl Sandburg
            Poetry(
                lines=[
                    "Hog Butcher for the World,",
                    "Tool Maker, Stacker of Wheat,",
                    "Player with Railroads and the Nation's Freight Handler;",
                    "Stormy, husky, brawling,"
                ],
                author="Carl Sandburg",
                title="Chicago",
                source="builtin"
            ),
            
            # e.e. cummings
            Poetry(
                lines=[
                    "i carry your heart with me(i carry it in",
                    "my heart)i am never without it(anywhere",
                    "i go you go,my dear;and whatever is done",
                    "by only me is your doing,my darling)"
                ],
                author="e.e. cummings",
                title="i carry your heart with me",
                source="builtin"
            ),
            
            # Rainer Maria Rilke
            Poetry(
                lines=[
                    "Perhaps all the dragons in our lives",
                    "are princesses who are only waiting to see us act,",
                    "just once, with beauty and courage.",
                    "Perhaps everything that frightens us is, in its deepest essence,"
                ],
                author="Rainer Maria Rilke",
                title="Letters to a Young Poet",
                source="builtin"
            ),
            
            # Pablo Neruda
            Poetry(
                lines=[
                    "I love you without knowing how, or when, or from where.",
                    "I love you straightforwardly, without complexities or pride;",
                    "so I love you because I don't know any other way",
                    "than this: where I does not exist, nor you,"
                ],
                author="Pablo Neruda",
                title="Sonnet XVII",
                source="builtin"
            ),
            
            # Khalil Gibran
            Poetry(
                lines=[
                    "Your children are not your children.",
                    "They are the sons and daughters of Life's longing for itself.",
                    "They come through you but not from you,",
                    "And though they are with you yet they belong not to you."
                ],
                author="Khalil Gibran",
                title="On Children",
                source="builtin"
            ),
            Poetry(
                lines=[
                    "And think not you can direct the course of love,",
                    "For love, if it finds you worthy, directs your course.",
                    "Love has no other desire but to fulfill itself.",
                    "But if you love and must needs have desires, let these be your desires:"
                ],
                author="Khalil Gibran",
                title="On Love",
                source="builtin"
            ),
            
            # Rabindranath Tagore
            Poetry(
                lines=[
                    "Where the mind is without fear and the head is held high",
                    "Where knowledge is free",
                    "Where the world has not been broken up into fragments",
                    "By narrow domestic walls"
                ],
                author="Rabindranath Tagore",
                title="Where The Mind Is Without Fear",
                source="builtin"
            ),
            
            # Mary Oliver
            Poetry(
                lines=[
                    "Tell me, what else should I have done?",
                    "Doesn't everything die at last, and too soon?",
                    "Tell me, what is it you plan to do",
                    "with your one wild and precious life?"
                ],
                author="Mary Oliver",
                title="The Summer Day",
                source="builtin"
            ),
            
            # Rumi
            Poetry(
                lines=[
                    "Out beyond ideas of wrongdoing and rightdoing,",
                    "there is a field. I'll meet you there.",
                    "When the soul lies down in that grass,",
                    "the world is too full to talk about."
                ],
                author="Rumi",
                title="Out Beyond Ideas",
                source="builtin"
            ),
            Poetry(
                lines=[
                    "Let yourself be silently drawn by the strange pull of what you really love.",
                    "It will not lead you astray.",
                    "What you seek is seeking you.",
                    "Yesterday I was clever, so I wanted to change the world."
                ],
                author="Rumi",
                title="What You Seek Is Seeking You",
                source="builtin"
            ),
            
            # Hafez
            Poetry(
                lines=[
                    "I wish I could show you,",
                    "When you are lonely or in darkness,",
                    "The astonishing light",
                    "Of your own being."
                ],
                author="Hafez",
                title="The Light of Your Own Being",
                source="builtin"
            ),
            
            # Li Bai
            Poetry(
                lines=[
                    "The birds have vanished into the sky,",
                    "and now the last cloud drains away.",
                    "We sit together, the mountain and me,",
                    "until only the mountain remains."
                ],
                author="Li Bai",
                title="Sitting Alone by Jingting Mountain",
                source="builtin"
            ),
            
            # Matsuo Bashō
            Poetry(
                lines=[
                    "An ancient pond—",
                    "a frog leaps in,",
                    "the sound of water.",
                    "Silent and serene."
                ],
                author="Matsuo Bashō",
                title="Ancient Pond",
                source="builtin"
            ),
            
            # Hafez
            Poetry(
                lines=[
                    "Even after all this time",
                    "The sun never says to the earth,",
                    "\"You owe me.\"",
                    "Look what happens with a love like that."
                ],
                author="Hafez",
                title="A Love Like That",
                source="builtin"
            ),
            
            # Anonymous/Traditional
            Poetry(
                lines=[
                    "Do not go gentle into that good night,",
                    "Old age should burn and rave at close of day;",
                    "Rage, rage against the dying of the light.",
                    "Though wise men at their end know dark is right,"
                ],
                author="Dylan Thomas",
                title="Do Not Go Gentle Into That Good Night",
                source="builtin"
            ),
            
            # Robert Louis Stevenson
            Poetry(
                lines=[
                    "I have a little shadow that goes in and out with me,",
                    "And what can be the use of him is more than I can see.",
                    "He is very, very like me from the heels up to the head;",
                    "And I see him jump before me, when I jump into my bed."
                ],
                author="Robert Louis Stevenson",
                title="My Shadow",
                source="builtin"
            ),
            
            # Joyce Kilmer
            Poetry(
                lines=[
                    "I think that I shall never see",
                    "A poem lovely as a tree.",
                    "A tree whose hungry mouth is prest",
                    "Against the earth's sweet flowing breast;"
                ],
                author="Joyce Kilmer",
                title="Trees",
                source="builtin"
            ),
            
            # Christina Rossetti
            Poetry(
                lines=[
                    "Remember me when I am gone away,",
                    "Gone far away into the silent land;",
                    "When you can no more hold me by the hand,",
                    "Nor I half turn to go yet turning stay."
                ],
                author="Christina Rossetti",
                title="Remember",
                source="builtin"
            ),
        ]
        
        self.poetry_database.extend(builtin_poems)
        logger.info(f"Added {len(builtin_poems)} built-in poems")
        
    async def _fetch_poetry_foundation(self):
        """Fetch poetry from Poetry Foundation (if available)."""
        # This would implement scraping from poetry sources
        # For now, we rely on built-in collection
        pass
        
    async def _fetch_public_domain_poetry(self):
        """Fetch public domain poetry from various sources."""
        # This would implement scraping from Project Gutenberg, etc.
        # For now, we rely on built-in collection
        pass
        
    async def recite_existing_poem_with_gpt(self, theme: str = "nature", poet_name: str = "Robert Frost") -> Optional[Poetry]:
        """Ask GPT to recite a less common poem by the specified poet."""
        try:
            # Get poet info
            poet_info = next((p for p in self.famous_poets if p["name"] == poet_name), self.famous_poets[0])
            
            # Craft the prompt to ask for less common poems
            prompt = f"""Please recite a less commonly known or underappreciated poem by {poet_info['name']} that relates to {theme}.\n\n
Requirements:
- Must be an actual, existing poem by {poet_info['name']}
- Should be 4-8 lines long (you can use a short excerpt if the poem is longer)
- Each line must be on a new line
- Return at least 4 lines
- Family-friendly and appropriate for all audiences
- Should relate to themes like {theme}
- Return ONLY the poem lines, no title or author attribution
- Avoid the poet's most famous works (e.g., for Robert Frost, avoid 'The Road Not Taken', 'Stopping by Woods', 'Fire and Ice', etc.)
- Choose lesser-known but authentic poems that showcase the poet's style

Respond with only the poem lines, one per line, no extra text."""

            # Make API request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.gpt_endpoint,
                    headers={
                        "api-key": self.gpt_api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        # "max_completion_tokens": 200,
                        "temperature": 1.0
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    poem_text = response.json()["choices"][0]["message"]["content"].strip()
                    logger.info(f"Raw GPT poem response: {poem_text}")
                    lines = [line.strip() for line in poem_text.split("\n") if line.strip()]
                    
                    # Clean up any quotation marks or formatting
                    clean_lines = []
                    for line in lines:
                        # Remove quotes and clean formatting
                        line = line.strip('"').strip("'").strip()
                        if line and not line.startswith("Title:") and not line.startswith("Author:"):
                            clean_lines.append(line)
                    
                    if len(clean_lines) >= 3:  # Allow shorter excerpts of famous poems
                        # Create Poetry object
                        poem = Poetry(
                            lines=clean_lines,
                            author=poet_info['name'],
                            title=f"Famous poem by {poet_info['name']}",
                            source="gpt_recited",
                            theme=theme,
                            created_at=datetime.now()
                        )
                        
                        logger.info(f"GPT recited existing poem by {poet_info['name']}")
                        return poem
                    else:
                        logger.warning(f"GPT response too short for poem: {poem_text}")
                        return None
                else:
                    logger.warning(f"Azure OpenAI GPT failed with status {response.status_code}: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to get GPT recited poem: {e}")
            return None
            
    async def get_poetry_for_theme(
        self,
        themes: List[str],
        min_lines: int = 4,
        max_lines: int = 8
    ) -> Poetry:
        """Get poetry matching specified themes (always use GPT first, never cache)."""
        theme_name = themes[0] if themes else "nature"
        try:
            poet = random.choice(self.famous_poets)
            gpt_poem = await self.recite_existing_poem_with_gpt(theme_name, poet["name"])
            if gpt_poem and min_lines <= len(gpt_poem.lines) <= max_lines:
                logger.info(f"Using existing poem recited by GPT: {poet['name']} - {gpt_poem.title}")
                return gpt_poem
        except Exception as e:
            logger.warning(f"Failed to get GPT recited poem: {e}")
        # Fallback to built-in poems only
        matching_poems = [
            poem for poem in self.poetry_database
            if min_lines <= len(poem.lines) <= max_lines
        ]
        if matching_poems:
            selected_poem = random.choice(matching_poems)
            logger.info(f"Selected poem from {selected_poem.source}: {selected_poem.title}")
            return selected_poem
        logger.warning("No matching poems found, using default")
        return Poetry(
            lines=[
                "In the forest deep and green,",
                "Where ancient trees have been,",
                "Nature's wisdom flows so free,",
                "Teaching all who wish to see."
            ],
            author="AI Default",
            title="Nature's Wisdom",
            source="default",
            theme="nature"
        )
            
    async def get_random_poetry(self) -> Poetry:
        """Get a random poetry from the database."""
        if self.poetry_database:
            return random.choice(self.poetry_database)
        else:
            return await self.get_poetry_for_theme(["peace"], 4, 8)
            
    async def add_custom_poetry(
        self,
        lines: List[str],
        author: Optional[str] = None,
        title: Optional[str] = None
    ) -> bool:
        """
        Add custom poetry to the database.
        
        Args:
            lines: Poetry lines
            author: Optional author name
            title: Optional title
            
        Returns:
            True if added successfully
        """
        try:
            poetry = Poetry(
                lines=lines,
                author=author,
                title=title,
                source="custom"
            )
            self.poetry_database.append(poetry)
            await self._save_poetry_cache()
            return True
        except Exception as e:
            logger.error(f"Failed to add custom poetry: {e}")
            return False 

    async def generate_poem_with_openai(self, theme: str = "nature", poet_style: str = "Robert Frost") -> Optional[Poetry]:
        """Get an existing famous poem using OpenAI based on theme and poet style."""
        if not self.openai_client:
            logger.warning("OpenAI client not available for poem selection")
            return None
            
        try:
            poet_info = next((p for p in self.famous_poets if p["name"] == poet_style), self.famous_poets[0])
            
            prompt = f"""Please recite a famous, well-known poem by {poet_info['name']} that relates to the theme of {theme}. 

Requirements:
- Must be an actual, existing poem by {poet_info['name']}
- Should be 4-8 lines long (you can use a short excerpt if the poem is longer)
- Family-friendly and appropriate for all audiences
- Should relate to themes like {theme}, nature, hope, love, dreams, or life's beauty
- Return ONLY the poem lines, no title or author attribution
- Do not generate new content - only recite existing famous poems

For example, if asked for Robert Frost and nature, you might recite lines from "The Road Not Taken" or "Stopping by Woods on a Snowy Evening"."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a poetry scholar who knows famous poems by heart. You only recite existing, well-known poems by famous poets. You never generate new content - only provide exact lines from real, published poems."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3  # Lower temperature for more consistent/accurate recitation
            )
            
            poem_text = response.choices[0].message.content.strip()
            lines = [line.strip() for line in poem_text.split('\n') if line.strip()]
            
            # Clean up any quotation marks or formatting
            clean_lines = []
            for line in lines:
                # Remove quotes and clean formatting
                line = line.strip('"').strip("'").strip()
                if line and not line.startswith("Title:") and not line.startswith("Author:"):
                    clean_lines.append(line)
            
            if len(clean_lines) >= 3:  # Allow shorter excerpts of famous poems
                poem = Poetry(
                    lines=clean_lines,
                    author=poet_info['name'],
                    title=f"{theme.title()} - {poet_info['name']} Excerpt",
                    source="famous_poem_recitation",
                    theme=theme,
                    created_at=datetime.now()
                )
                
                logger.info(f"Selected famous poem by {poet_info['name']}: {poem.title}")
                return poem
                
        except Exception as e:
            logger.error(f"Failed to get famous poem with OpenAI: {e}")
            
        return None 