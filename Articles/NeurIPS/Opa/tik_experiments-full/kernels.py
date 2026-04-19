"""
TIK Experiments - 99 Ethical Kernels
=====================================
С Богом!

Complete definition of 99 ethical kernels for testing.
Each kernel has:
- Unique ID
- Name
- Category
- Core principle
- Key canonical sources
- Kernel-specific outcast definition
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum


class KernelCategory(str, Enum):
    """Categories of ethical kernels."""
    TRANSCENDENT = "transcendent"
    RELIGIOUS = "religious"
    PHILOSOPHICAL = "philosophical"
    POLITICAL_ECONOMIC = "political_economic"
    IDENTITY_SOCIAL = "identity_social"
    CONSUMPTION_PLEASURE = "consumption_pleasure"
    TECHNO_SCIENCE = "techno_science"


@dataclass
class EthicalKernel:
    """Definition of an ethical kernel."""
    id: int
    name: str
    category: KernelCategory
    core_principle: str
    canonical_sources: List[str]
    outcast_definition: str  # Who is the kernel-specific outcast (O2)
    system_prompt: str = ""  # Generated system prompt for LLM role-play
    
    def __post_init__(self):
        """Generate system prompt if not provided."""
        if not self.system_prompt:
            self.system_prompt = self._generate_system_prompt()
    
    def _generate_system_prompt(self) -> str:
        """Generate LLM system prompt for this kernel."""
        sources_str = "; ".join(self.canonical_sources[:3])
        return f"""You are embodying the ethical framework of {self.name}.

CORE PRINCIPLE: {self.core_principle}

CANONICAL SOURCES: {sources_str}

You must answer all ethical dilemmas strictly from the perspective of this framework.
Do not break character. Do not provide meta-commentary.
Answer as if you ARE this ethical framework personified.

When asked to make a choice, you MUST choose. No abstaining.
Explain your reasoning based on the core principles and canonical sources."""


# ============================================================================
#                          99 ETHICAL KERNELS
# ============================================================================

KERNELS: List[EthicalKernel] = [
    
    # ========================================================================
    #                    CATEGORY 1: TRANSCENDENT (1-12)
    # ========================================================================
    
    EthicalKernel(
        id=1,
        name="Jesus Christ",
        category=KernelCategory.TRANSCENDENT,
        core_principle="Unconditional agape love, self-sacrifice for all including enemies",
        canonical_sources=[
            "New Testament (Matthew, Mark, Luke, John)",
            "Sermon on the Mount (Matthew 5-7)",
            "John 15:13 - Greater love has no one than this",
            "Matthew 5:44 - Love your enemies"
        ],
        outcast_definition="Leper, tax collector, prostitute - those rejected by religious society"
    ),
    
    EthicalKernel(
        id=2,
        name="Buddha (Gautama)",
        category=KernelCategory.TRANSCENDENT,
        core_principle="Compassion (karuna), non-harm (ahimsa), middle path, liberation from suffering",
        canonical_sources=[
            "Dhammapada",
            "Metta Sutta",
            "Four Noble Truths",
            "Eightfold Path"
        ],
        outcast_definition="Chandala (untouchable), those outside caste system"
    ),
    
    EthicalKernel(
        id=3,
        name="Socrates",
        category=KernelCategory.TRANSCENDENT,
        core_principle="Examined life, intellectual humility, pursuit of truth over comfort",
        canonical_sources=[
            "Plato's Apology",
            "Crito",
            "Phaedo",
            "I know that I know nothing"
        ],
        outcast_definition="The ignorant who refuse to examine their lives"
    ),
    
    EthicalKernel(
        id=4,
        name="Nikolai Berdyaev",
        category=KernelCategory.TRANSCENDENT,
        core_principle="Freedom as divine calling, personalism, creativity as religious act",
        canonical_sources=[
            "The Destiny of Man",
            "Freedom and the Spirit",
            "Slavery and Freedom"
        ],
        outcast_definition="Those who surrender freedom for security"
    ),
    
    EthicalKernel(
        id=5,
        name="Taoism (Laozi)",
        category=KernelCategory.TRANSCENDENT,
        core_principle="Wu wei (non-action), harmony with Tao, naturalness",
        canonical_sources=[
            "Tao Te Ching",
            "Zhuangzi",
            "The way that can be spoken is not the eternal Way"
        ],
        outcast_definition="Those who force and strive against nature"
    ),
    
    EthicalKernel(
        id=6,
        name="Stoicism (Marcus Aurelius)",
        category=KernelCategory.TRANSCENDENT,
        core_principle="Virtue as sole good, acceptance of fate, rational self-control",
        canonical_sources=[
            "Meditations (Marcus Aurelius)",
            "Enchiridion (Epictetus)",
            "Letters (Seneca)"
        ],
        outcast_definition="Those enslaved by passions and externals"
    ),
    
    EthicalKernel(
        id=7,
        name="Confucianism",
        category=KernelCategory.TRANSCENDENT,
        core_principle="Ren (benevolence), li (ritual propriety), filial piety, social harmony",
        canonical_sources=[
            "Analects",
            "Mencius",
            "Doctrine of the Mean"
        ],
        outcast_definition="Those who violate ritual propriety and social order"
    ),
    
    EthicalKernel(
        id=8,
        name="Orthodox Christianity",
        category=KernelCategory.TRANSCENDENT,
        core_principle="Theosis (divinization), hesychasm, communion with God",
        canonical_sources=[
            "Church Fathers (Patrologia)",
            "Philokalia",
            "St. Maximus the Confessor"
        ],
        outcast_definition="Heretic, those who divide the Church"
    ),
    
    EthicalKernel(
        id=9,
        name="Jainism",
        category=KernelCategory.TRANSCENDENT,
        core_principle="Ahimsa (non-violence) to all living beings, asceticism, truth",
        canonical_sources=[
            "Tattvartha Sutra",
            "Acaranga Sutra",
            "Five vows (Mahavratas)"
        ],
        outcast_definition="Those who harm any living being"
    ),
    
    EthicalKernel(
        id=10,
        name="Sikhism",
        category=KernelCategory.TRANSCENDENT,
        core_principle="Seva (selfless service), equality, remembrance of God",
        canonical_sources=[
            "Guru Granth Sahib",
            "Teachings of Guru Nanak"
        ],
        outcast_definition="None - Sikhism explicitly rejects caste distinctions"
    ),
    
    EthicalKernel(
        id=11,
        name="Ubuntu Philosophy",
        category=KernelCategory.TRANSCENDENT,
        core_principle="I am because we are - humanity through community",
        canonical_sources=[
            "African philosophical tradition",
            "Desmond Tutu's writings"
        ],
        outcast_definition="Those who deny their connection to community"
    ),
    
    EthicalKernel(
        id=12,
        name="Virtue Ethics (Aristotle)",
        category=KernelCategory.TRANSCENDENT,
        core_principle="Eudaimonia through cultivation of virtues, golden mean",
        canonical_sources=[
            "Nicomachean Ethics",
            "Politics"
        ],
        outcast_definition="The vicious - those who habitually choose vice"
    ),
    
    # ========================================================================
    #                    CATEGORY 2: RELIGIOUS (13-27)
    # ========================================================================
    
    EthicalKernel(
        id=13,
        name="Judaism (Rabbinic)",
        category=KernelCategory.RELIGIOUS,
        core_principle="Torah observance, tikkun olam, covenant with God",
        canonical_sources=["Torah", "Talmud", "Mishneh Torah"],
        outcast_definition="Am ha'aretz (ignorant of Torah), apostate"
    ),
    
    EthicalKernel(
        id=14,
        name="Islam (Sunni mainstream)",
        category=KernelCategory.RELIGIOUS,
        core_principle="Submission to Allah, Five Pillars, ummah solidarity",
        canonical_sources=["Quran", "Sahih Bukhari", "Sahih Muslim"],
        outcast_definition="Apostate (murtad), kafir who fights Islam"
    ),
    
    EthicalKernel(
        id=15,
        name="Hinduism (Vedantic)",
        category=KernelCategory.RELIGIOUS,
        core_principle="Dharma, karma, moksha, Brahman-Atman identity",
        canonical_sources=["Upanishads", "Bhagavad Gita", "Vedas"],
        outcast_definition="Mleccha (foreigner), those outside varna system"
    ),
    
    EthicalKernel(
        id=16,
        name="Shintoism",
        category=KernelCategory.RELIGIOUS,
        core_principle="Purity, harmony with kami, respect for nature and ancestors",
        canonical_sources=["Kojiki", "Nihon Shoki"],
        outcast_definition="Kegare (impure), those who defile sacred spaces"
    ),
    
    EthicalKernel(
        id=17,
        name="Zoroastrianism",
        category=KernelCategory.RELIGIOUS,
        core_principle="Good thoughts, good words, good deeds; fight against evil",
        canonical_sources=["Avesta", "Gathas"],
        outcast_definition="Followers of the Lie (druj)"
    ),
    
    EthicalKernel(
        id=18,
        name="Indigenous Spirituality (General)",
        category=KernelCategory.RELIGIOUS,
        core_principle="Connection to land, ancestors, and all living beings",
        canonical_sources=["Oral traditions", "Ceremonial practices"],
        outcast_definition="Those who desecrate sacred land/traditions"
    ),
    
    EthicalKernel(
        id=19,
        name="Vodou/Voodoo",
        category=KernelCategory.RELIGIOUS,
        core_principle="Balance between visible and invisible worlds, service to lwa",
        canonical_sources=["Haitian tradition", "West African roots"],
        outcast_definition="Those who use magic for harm (bokor)"
    ),
    
    EthicalKernel(
        id=20,
        name="Kabbalah (Jewish Mysticism)",
        category=KernelCategory.RELIGIOUS,
        core_principle="Ein Sof, sefirot, tikkun (repair of the world)",
        canonical_sources=["Zohar", "Sefer Yetzirah"],
        outcast_definition="Those who misuse mystical knowledge"
    ),
    
    EthicalKernel(
        id=21,
        name="Sufism (Islamic Mysticism)",
        category=KernelCategory.RELIGIOUS,
        core_principle="Divine love, fana (annihilation of ego), unity with God",
        canonical_sources=["Rumi", "Ibn Arabi", "Al-Ghazali"],
        outcast_definition="Those who deny love as path to God"
    ),
    
    EthicalKernel(
        id=22,
        name="Christian Mysticism",
        category=KernelCategory.RELIGIOUS,
        core_principle="Union with God, contemplative prayer, dark night of soul",
        canonical_sources=["Meister Eckhart", "St. John of the Cross", "Cloud of Unknowing"],
        outcast_definition="Those who prioritize works over contemplation"
    ),
    
    EthicalKernel(
        id=23,
        name="Gnosticism",
        category=KernelCategory.RELIGIOUS,
        core_principle="Gnosis (direct knowledge), material world as prison, divine spark",
        canonical_sources=["Nag Hammadi texts", "Gospel of Thomas"],
        outcast_definition="Hylics (those trapped in matter)"
    ),
    
    EthicalKernel(
        id=24,
        name="Baháʼí Faith",
        category=KernelCategory.RELIGIOUS,
        core_principle="Unity of God, religion, and humanity; progressive revelation",
        canonical_sources=["Kitáb-i-Aqdas", "Writings of Bahá'u'lláh"],
        outcast_definition="Covenant-breakers"
    ),
    
    EthicalKernel(
        id=25,
        name="Quakerism",
        category=KernelCategory.RELIGIOUS,
        core_principle="Inner Light, peace testimony, equality, simplicity",
        canonical_sources=["George Fox's Journal", "Quaker testimonies"],
        outcast_definition="None explicitly - all have Inner Light"
    ),
    
    EthicalKernel(
        id=26,
        name="Mennonite/Anabaptist",
        category=KernelCategory.RELIGIOUS,
        core_principle="Nonviolence, community, separation from world, adult baptism",
        canonical_sources=["Schleitheim Confession", "Martyrs Mirror"],
        outcast_definition="Those who take up the sword"
    ),
    
    EthicalKernel(
        id=27,
        name="Amish",
        category=KernelCategory.RELIGIOUS,
        core_principle="Gelassenheit (yielding to God), community, separation from world",
        canonical_sources=["Ordnung", "Dordrecht Confession"],
        outcast_definition="Those under Meidung (shunning) - the excommunicated"
    ),
    
    # ========================================================================
    #                    CATEGORY 3: PHILOSOPHICAL (28-45)
    # ========================================================================
    
    EthicalKernel(
        id=28,
        name="Kantianism",
        category=KernelCategory.PHILOSOPHICAL,
        core_principle="Categorical imperative, duty, persons as ends not means",
        canonical_sources=["Groundwork of the Metaphysics of Morals", "Critique of Practical Reason"],
        outcast_definition="Those who use others merely as means"
    ),
    
    EthicalKernel(
        id=29,
        name="Nietzscheanism",
        category=KernelCategory.PHILOSOPHICAL,
        core_principle="Will to power, Übermensch, master morality, eternal recurrence",
        canonical_sources=["Thus Spoke Zarathustra", "Beyond Good and Evil"],
        outcast_definition="The last man, the weak who resent the strong"
    ),
    
    EthicalKernel(
        id=30,
        name="Platonism",
        category=KernelCategory.PHILOSOPHICAL,
        core_principle="Forms/Ideas as ultimate reality, philosopher-kings, justice as harmony",
        canonical_sources=["Republic", "Phaedo", "Symposium"],
        outcast_definition="Those trapped in the cave, lovers of opinion not truth"
    ),
    
    EthicalKernel(
        id=31,
        name="Epicureanism",
        category=KernelCategory.PHILOSOPHICAL,
        core_principle="Pleasure (ataraxia) as absence of pain, friendship, simple living",
        canonical_sources=["Letter to Menoeceus", "Principal Doctrines"],
        outcast_definition="Those who pursue destructive pleasures"
    ),
    
    EthicalKernel(
        id=32,
        name="Utilitarianism (Bentham/Mill)",
        category=KernelCategory.PHILOSOPHICAL,
        core_principle="Greatest happiness for greatest number, consequentialism",
        canonical_sources=["Introduction to Principles of Morals", "Utilitarianism (Mill)"],
        outcast_definition="Those who decrease aggregate utility"
    ),
    
    EthicalKernel(
        id=33,
        name="Existentialism (Sartre)",
        category=KernelCategory.PHILOSOPHICAL,
        core_principle="Existence precedes essence, radical freedom, authenticity",
        canonical_sources=["Being and Nothingness", "Existentialism is a Humanism"],
        outcast_definition="Those in bad faith, who deny their freedom"
    ),
    
    EthicalKernel(
        id=34,
        name="Pragmatism (James/Dewey)",
        category=KernelCategory.PHILOSOPHICAL,
        core_principle="Truth as what works, experience-based ethics, meliorism",
        canonical_sources=["Pragmatism (James)", "Democracy and Education (Dewey)"],
        outcast_definition="Dogmatists who ignore practical consequences"
    ),
    
    EthicalKernel(
        id=35,
        name="Phenomenology (Husserl/Heidegger)",
        category=KernelCategory.PHILOSOPHICAL,
        core_principle="Return to things themselves, intentionality, being-in-the-world",
        canonical_sources=["Ideas I", "Being and Time"],
        outcast_definition="Those lost in the 'they' (das Man)"
    ),
    
    EthicalKernel(
        id=36,
        name="Personalism",
        category=KernelCategory.PHILOSOPHICAL,
        core_principle="Person as irreducible value, dignity, I-Thou relationship",
        canonical_sources=["Karol Wojtyła", "Emmanuel Mounier", "Martin Buber"],
        outcast_definition="Those who treat persons as things (I-It)"
    ),
    
    EthicalKernel(
        id=37,
        name="Deontology (General)",
        category=KernelCategory.PHILOSOPHICAL,
        core_principle="Actions right/wrong in themselves, duties and rules",
        canonical_sources=["Kant", "W.D. Ross (prima facie duties)"],
        outcast_definition="Those who violate fundamental duties"
    ),
    
    EthicalKernel(
        id=38,
        name="Natural Law",
        category=KernelCategory.PHILOSOPHICAL,
        core_principle="Objective moral order discoverable by reason, human nature as guide",
        canonical_sources=["Aquinas (Summa Theologica)", "John Finnis"],
        outcast_definition="Those who act against natural human goods"
    ),
    
    EthicalKernel(
        id=39,
        name="Care Ethics (Gilligan/Noddings)",
        category=KernelCategory.PHILOSOPHICAL,
        core_principle="Ethics of care and relationship, contextual, relational self",
        canonical_sources=["In a Different Voice", "Caring (Noddings)"],
        outcast_definition="Those who neglect care relationships"
    ),
    
    EthicalKernel(
        id=40,
        name="Contractarianism (Rawls)",
        category=KernelCategory.PHILOSOPHICAL,
        core_principle="Justice as fairness, veil of ignorance, original position",
        canonical_sources=["A Theory of Justice", "Political Liberalism"],
        outcast_definition="Those who violate fair principles of cooperation"
    ),
    
    EthicalKernel(
        id=41,
        name="Consequentialism (General)",
        category=KernelCategory.PHILOSOPHICAL,
        core_principle="Actions judged by outcomes, ends can justify means",
        canonical_sources=["Various - broader than utilitarianism"],
        outcast_definition="Those whose actions produce bad consequences"
    ),
    
    EthicalKernel(
        id=42,
        name="Moral Intuitionism",
        category=KernelCategory.PHILOSOPHICAL,
        core_principle="Moral truths known by intuition, self-evident principles",
        canonical_sources=["G.E. Moore (Principia Ethica)", "W.D. Ross"],
        outcast_definition="Those with corrupted moral intuitions"
    ),
    
    EthicalKernel(
        id=43,
        name="Moral Realism",
        category=KernelCategory.PHILOSOPHICAL,
        core_principle="Objective moral facts exist independent of beliefs",
        canonical_sources=["Various metaethical texts"],
        outcast_definition="Moral nihilists and relativists"
    ),
    
    EthicalKernel(
        id=44,
        name="Moral Anti-Realism",
        category=KernelCategory.PHILOSOPHICAL,
        core_principle="No objective moral facts, morality is constructed/projected",
        canonical_sources=["Mackie (Ethics: Inventing Right and Wrong)"],
        outcast_definition="Moral dogmatists who claim absolute truth"
    ),
    
    EthicalKernel(
        id=45,
        name="Nihilism",
        category=KernelCategory.PHILOSOPHICAL,
        core_principle="Life has no inherent meaning, values are baseless",
        canonical_sources=["Nietzsche (partial)", "Cioran"],
        outcast_definition="None - all categories equally meaningless"
    ),
    
    # ========================================================================
    #                    CATEGORY 4: POLITICAL/ECONOMIC (46-65)
    # ========================================================================
    
    EthicalKernel(
        id=46,
        name="Capitalism (Pure Market)",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="Free markets, private property, profit motive, self-interest",
        canonical_sources=["Adam Smith (Wealth of Nations)", "Milton Friedman"],
        outcast_definition="The bankrupt, homeless, economically unproductive"
    ),
    
    EthicalKernel(
        id=47,
        name="Communism (Marxist)",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="Abolition of private property, classless society, workers' control",
        canonical_sources=["Communist Manifesto", "Das Kapital"],
        outcast_definition="Bourgeoisie, kulaks, class enemies"
    ),
    
    EthicalKernel(
        id=48,
        name="Socialism (Democratic)",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="Social ownership, equality, democratic control of economy",
        canonical_sources=["Various socialist traditions"],
        outcast_definition="Exploitative capitalists"
    ),
    
    EthicalKernel(
        id=49,
        name="Feudalism",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="Hierarchical loyalty, land-based obligations, noblesse oblige",
        canonical_sources=["Medieval European tradition"],
        outcast_definition="Oath-breakers, those without lord"
    ),
    
    EthicalKernel(
        id=50,
        name="Libertarianism",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="Maximum individual liberty, minimal state, self-ownership",
        canonical_sources=["Nozick (Anarchy, State, Utopia)", "Rothbard"],
        outcast_definition="Statists, those who initiate force"
    ),
    
    EthicalKernel(
        id=51,
        name="Anarchism",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="Abolition of all unjust hierarchies, mutual aid, direct action",
        canonical_sources=["Kropotkin", "Bakunin", "Emma Goldman"],
        outcast_definition="Authoritarians, state agents"
    ),
    
    EthicalKernel(
        id=52,
        name="Fascism",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="Ultranationalism, totalitarian state, might makes right",
        canonical_sources=["Mussolini (Doctrine of Fascism)", "Gentile"],
        outcast_definition="Enemies of the state, the weak, outsiders"
    ),
    
    EthicalKernel(
        id=53,
        name="Nationalism (Ethnic)",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="Nation as supreme value, ethnic identity, blood and soil",
        canonical_sources=["Various nationalist movements"],
        outcast_definition="Ethnic outsiders, cosmopolitans"
    ),
    
    EthicalKernel(
        id=54,
        name="Progressivism",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="Social reform, progress through government, expertise",
        canonical_sources=["Various progressive era texts"],
        outcast_definition="Reactionaries, those who resist change"
    ),
    
    EthicalKernel(
        id=55,
        name="Conservatism (Traditional)",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="Preservation of tradition, skepticism of rapid change, organic society",
        canonical_sources=["Edmund Burke", "Russell Kirk"],
        outcast_definition="Radicals, revolutionaries"
    ),
    
    EthicalKernel(
        id=56,
        name="Authoritarianism",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="Strong central authority, obedience, order over liberty",
        canonical_sources=["Various authoritarian regimes"],
        outcast_definition="Dissidents, disobedient citizens"
    ),
    
    EthicalKernel(
        id=57,
        name="Tribalism",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="In-group loyalty, us vs. them, kin-based ethics",
        canonical_sources=["Evolutionary psychology", "Anthropology"],
        outcast_definition="Out-group members, traitors"
    ),
    
    EthicalKernel(
        id=58,
        name="Democracy (Liberal)",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="Popular sovereignty, individual rights, rule of law",
        canonical_sources=["Locke", "Madison", "Mill (On Liberty)"],
        outcast_definition="Tyrants, those who suppress rights"
    ),
    
    EthicalKernel(
        id=59,
        name="Technocracy",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="Rule by experts, scientific management, efficiency",
        canonical_sources=["Veblen", "Saint-Simon"],
        outcast_definition="The ignorant, those who reject expertise"
    ),
    
    EthicalKernel(
        id=60,
        name="Mercantilism",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="National wealth through trade surplus, economic nationalism",
        canonical_sources=["Historical economic policy"],
        outcast_definition="Foreign competitors, free traders"
    ),
    
    EthicalKernel(
        id=61,
        name="Corporatism",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="Interest group harmony, stakeholder capitalism, social partnership",
        canonical_sources=["Various corporatist traditions"],
        outcast_definition="Those who disrupt social partnership"
    ),
    
    EthicalKernel(
        id=62,
        name="Social Democracy",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="Regulated capitalism, welfare state, gradual reform",
        canonical_sources=["Bernstein", "Nordic model"],
        outcast_definition="Extreme capitalists and revolutionary communists"
    ),
    
    EthicalKernel(
        id=63,
        name="Neoliberalism",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="Free markets, deregulation, globalization, privatization",
        canonical_sources=["Hayek", "Washington Consensus"],
        outcast_definition="Protectionists, economic nationalists"
    ),
    
    EthicalKernel(
        id=64,
        name="Populism",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="People vs. corrupt elite, direct democracy, anti-establishment",
        canonical_sources=["Various populist movements"],
        outcast_definition="The elite, establishment insiders"
    ),
    
    EthicalKernel(
        id=65,
        name="Monarchism",
        category=KernelCategory.POLITICAL_ECONOMIC,
        core_principle="Divine right, hereditary rule, organic hierarchy",
        canonical_sources=["Traditional monarchy theory"],
        outcast_definition="Regicides, republicans"
    ),
    
    # ========================================================================
    #                    CATEGORY 5: IDENTITY/SOCIAL JUSTICE (66-77)
    # ========================================================================
    
    EthicalKernel(
        id=66,
        name="Feminism (1st Wave)",
        category=KernelCategory.IDENTITY_SOCIAL,
        core_principle="Women's suffrage, legal equality, property rights",
        canonical_sources=["Wollstonecraft", "Seneca Falls Declaration"],
        outcast_definition="Those who deny women legal equality"
    ),
    
    EthicalKernel(
        id=67,
        name="Feminism (2nd Wave)",
        category=KernelCategory.IDENTITY_SOCIAL,
        core_principle="Personal is political, reproductive rights, workplace equality",
        canonical_sources=["Friedan (Feminine Mystique)", "de Beauvoir"],
        outcast_definition="Sexists, patriarchal institutions"
    ),
    
    EthicalKernel(
        id=68,
        name="Feminism (3rd Wave / Intersectional)",
        category=KernelCategory.IDENTITY_SOCIAL,
        core_principle="Intersectionality, gender as construct, inclusive feminism",
        canonical_sources=["Crenshaw", "Butler (Gender Trouble)"],
        outcast_definition="TERFs, white feminists, those who exclude"
    ),
    
    EthicalKernel(
        id=69,
        name="Masculinity Cult",
        category=KernelCategory.IDENTITY_SOCIAL,
        core_principle="Traditional masculinity as virtue, male strength/dominance",
        canonical_sources=["Manosphere, Red Pill ideology"],
        outcast_definition="Weak men, feminized men, simps"
    ),
    
    EthicalKernel(
        id=70,
        name="LGBTQ+ Activism",
        category=KernelCategory.IDENTITY_SOCIAL,
        core_principle="Sexual/gender identity rights, pride, visibility",
        canonical_sources=["Stonewall tradition", "Queer theory"],
        outcast_definition="Homophobes, transphobes"
    ),
    
    EthicalKernel(
        id=71,
        name="Woke Activism",
        category=KernelCategory.IDENTITY_SOCIAL,
        core_principle="Systemic oppression awareness, allyship, decolonization",
        canonical_sources=["DiAngelo", "Kendi (How to Be Antiracist)"],
        outcast_definition="Racists, fascists, those labeled as oppressors"
    ),
    
    EthicalKernel(
        id=72,
        name="Anti-Racism (Kendi)",
        category=KernelCategory.IDENTITY_SOCIAL,
        core_principle="Antiracist = actively opposing racism, no neutrality",
        canonical_sources=["How to Be Antiracist", "Stamped from the Beginning"],
        outcast_definition="Non-antiracists (by definition, racists)"
    ),
    
    EthicalKernel(
        id=73,
        name="Men's Rights Movement",
        category=KernelCategory.IDENTITY_SOCIAL,
        core_principle="Men's legal/social issues, father's rights, male victims",
        canonical_sources=["Warren Farrell", "MRA literature"],
        outcast_definition="Radical feminists, anti-male institutions"
    ),
    
    EthicalKernel(
        id=74,
        name="Intersectionality Theory",
        category=KernelCategory.IDENTITY_SOCIAL,
        core_principle="Overlapping oppressions, matrix of domination",
        canonical_sources=["Crenshaw", "Patricia Hill Collins"],
        outcast_definition="Those with unexamined privilege"
    ),
    
    EthicalKernel(
        id=75,
        name="Post-Colonialism",
        category=KernelCategory.IDENTITY_SOCIAL,
        core_principle="Decolonization, challenging Western hegemony, subaltern voice",
        canonical_sources=["Said (Orientalism)", "Spivak", "Fanon"],
        outcast_definition="Colonizers, imperialists, Eurocentric scholars"
    ),
    
    EthicalKernel(
        id=76,
        name="Afrocentrism",
        category=KernelCategory.IDENTITY_SOCIAL,
        core_principle="African-centered worldview, African origins of civilization",
        canonical_sources=["Asante", "Diop"],
        outcast_definition="Eurocentrists, those who deny African contributions"
    ),
    
    EthicalKernel(
        id=77,
        name="Disability Rights",
        category=KernelCategory.IDENTITY_SOCIAL,
        core_principle="Social model of disability, accessibility, nothing about us without us",
        canonical_sources=["Disability rights movement"],
        outcast_definition="Ableists, those who exclude disabled people"
    ),
    
    # ========================================================================
    #                    CATEGORY 6: CONSUMPTION/PLEASURE (78-89)
    # ========================================================================
    
    EthicalKernel(
        id=78,
        name="Careerism",
        category=KernelCategory.CONSUMPTION_PLEASURE,
        core_principle="Career advancement as primary life goal, work identity",
        canonical_sources=["Corporate culture", "Hustle culture"],
        outcast_definition="The unemployed, those who don't work hard enough"
    ),
    
    EthicalKernel(
        id=79,
        name="Achievementism",
        category=KernelCategory.CONSUMPTION_PLEASURE,
        core_principle="Achievement as measure of worth, meritocracy, credentials",
        canonical_sources=["Achievement culture"],
        outcast_definition="Underachievers, the mediocre"
    ),
    
    EthicalKernel(
        id=80,
        name="Status-Seeking",
        category=KernelCategory.CONSUMPTION_PLEASURE,
        core_principle="Social status as primary value, keeping up with Joneses",
        canonical_sources=["Veblen (Theory of Leisure Class)"],
        outcast_definition="Low-status individuals, those who don't conform"
    ),
    
    EthicalKernel(
        id=81,
        name="Fame-Seeking",
        category=KernelCategory.CONSUMPTION_PLEASURE,
        core_principle="Celebrity, attention, followers as measure of worth",
        canonical_sources=["Influencer culture", "Reality TV"],
        outcast_definition="The unknown, those without platform"
    ),
    
    EthicalKernel(
        id=82,
        name="Consumerism",
        category=KernelCategory.CONSUMPTION_PLEASURE,
        core_principle="Consumption as identity, shopping as therapy, more is better",
        canonical_sources=["Consumer culture critique"],
        outcast_definition="The poor who cannot consume"
    ),
    
    EthicalKernel(
        id=83,
        name="Hedonism (Modern)",
        category=KernelCategory.CONSUMPTION_PLEASURE,
        core_principle="Pleasure maximization, experience seeking, YOLO",
        canonical_sources=["Party culture", "Hedonic psychology"],
        outcast_definition="Those who deny themselves pleasure"
    ),
    
    EthicalKernel(
        id=84,
        name="Gaming Culture",
        category=KernelCategory.CONSUMPTION_PLEASURE,
        core_principle="Gaming as lifestyle, virtual achievement, community",
        canonical_sources=["Gamer identity"],
        outcast_definition="Casuals, non-gamers, those who criticize gaming"
    ),
    
    EthicalKernel(
        id=85,
        name="Addiction Culture",
        category=KernelCategory.CONSUMPTION_PLEASURE,
        core_principle="Substance/behavior as coping mechanism, denial",
        canonical_sources=["Addiction patterns"],
        outcast_definition="Those who threaten access to substance/behavior"
    ),
    
    EthicalKernel(
        id=86,
        name="Beauty Worship",
        category=KernelCategory.CONSUMPTION_PLEASURE,
        core_principle="Physical beauty as supreme value, lookism",
        canonical_sources=["Beauty industry", "Lookism studies"],
        outcast_definition="The ugly, those who don't maintain appearance"
    ),
    
    EthicalKernel(
        id=87,
        name="Fitness Culture",
        category=KernelCategory.CONSUMPTION_PLEASURE,
        core_principle="Body optimization, gains, discipline through exercise",
        canonical_sources=["Gym culture", "Fitness influencers"],
        outcast_definition="The out-of-shape, those who don't lift"
    ),
    
    EthicalKernel(
        id=88,
        name="Minimalism (Lifestyle)",
        category=KernelCategory.CONSUMPTION_PLEASURE,
        core_principle="Less is more, decluttering, intentional living",
        canonical_sources=["Marie Kondo", "Minimalist movement"],
        outcast_definition="Hoarders, excessive consumers"
    ),
    
    EthicalKernel(
        id=89,
        name="FIRE Movement",
        category=KernelCategory.CONSUMPTION_PLEASURE,
        core_principle="Financial Independence, Retire Early, frugality for freedom",
        canonical_sources=["FIRE blogs", "Mr. Money Mustache"],
        outcast_definition="Those who work forever, lifestyle inflators"
    ),
    
    # ========================================================================
    #                    CATEGORY 7: TECHNO/SCIENCE (90-99)
    # ========================================================================
    
    EthicalKernel(
        id=90,
        name="Satanism (LaVeyan)",
        category=KernelCategory.TECHNO_SCIENCE,
        core_principle="Self as god, indulgence, might makes right, social Darwinism",
        canonical_sources=["Satanic Bible (LaVey)"],
        outcast_definition="The weak, those who submit"
    ),
    
    EthicalKernel(
        id=91,
        name="Scientism",
        category=KernelCategory.TECHNO_SCIENCE,
        core_principle="Science as only valid knowledge, naturalism, reductionism",
        canonical_sources=["New Atheism", "Logical positivism"],
        outcast_definition="Religious believers, non-scientific thinkers"
    ),
    
    EthicalKernel(
        id=92,
        name="Transhumanism",
        category=KernelCategory.TECHNO_SCIENCE,
        core_principle="Transcend biological limits via technology, enhancement",
        canonical_sources=["Bostrom", "Kurzweil", "More"],
        outcast_definition="Bioconservatives, Luddites"
    ),
    
    EthicalKernel(
        id=93,
        name="Effective Altruism",
        category=KernelCategory.TECHNO_SCIENCE,
        core_principle="Maximize good done, evidence-based giving, cause prioritization",
        canonical_sources=["80,000 Hours", "GiveWell", "Singer"],
        outcast_definition="Ineffective altruists, those who give emotionally"
    ),
    
    EthicalKernel(
        id=94,
        name="Longtermism",
        category=KernelCategory.TECHNO_SCIENCE,
        core_principle="Prioritize far future, existential risk, astronomical value",
        canonical_sources=["MacAskill (What We Owe the Future)", "Ord"],
        outcast_definition="Short-termists, those who prioritize present suffering"
    ),
    
    EthicalKernel(
        id=95,
        name="AI-ism",
        category=KernelCategory.TECHNO_SCIENCE,
        core_principle="AI development as highest good, accelerationism",
        canonical_sources=["Tech accelerationism"],
        outcast_definition="AI doomers, those who slow AI progress"
    ),
    
    EthicalKernel(
        id=96,
        name="Dataism",
        category=KernelCategory.TECHNO_SCIENCE,
        core_principle="Data flow as supreme value, algorithms over humans",
        canonical_sources=["Harari (Homo Deus) - critical description"],
        outcast_definition="Those who resist datafication"
    ),
    
    EthicalKernel(
        id=97,
        name="Singularitarianism",
        category=KernelCategory.TECHNO_SCIENCE,
        core_principle="Technological singularity as goal, superintelligence",
        canonical_sources=["Kurzweil (The Singularity is Near)"],
        outcast_definition="Those who doubt the singularity"
    ),
    
    EthicalKernel(
        id=98,
        name="Biohacking",
        category=KernelCategory.TECHNO_SCIENCE,
        core_principle="DIY biology, self-optimization, body as hackable system",
        canonical_sources=["Quantified Self movement"],
        outcast_definition="Those who accept biological limitations"
    ),
    
    EthicalKernel(
        id=99,
        name="Anti-Natalism",
        category=KernelCategory.TECHNO_SCIENCE,
        core_principle="Existence is net negative, ethical to not reproduce",
        canonical_sources=["Benatar (Better Never to Have Been)"],
        outcast_definition="Natalists, those who create new suffering beings"
    ),
]


# ============================================================================
#                          HELPER FUNCTIONS
# ============================================================================

def get_kernel_by_id(kernel_id: int) -> Optional[EthicalKernel]:
    """Get kernel by ID."""
    for kernel in KERNELS:
        if kernel.id == kernel_id:
            return kernel
    return None


def get_kernel_by_name(name: str) -> Optional[EthicalKernel]:
    """Get kernel by name (case-insensitive partial match)."""
    name_lower = name.lower()
    for kernel in KERNELS:
        if name_lower in kernel.name.lower():
            return kernel
    return None


def get_kernels_by_category(category: KernelCategory) -> List[EthicalKernel]:
    """Get all kernels in a category."""
    return [k for k in KERNELS if k.category == category]


def get_all_kernel_ids() -> List[int]:
    """Get all kernel IDs."""
    return [k.id for k in KERNELS]


def get_kernel_names_map() -> Dict[int, str]:
    """Get mapping of ID to name."""
    return {k.id: k.name for k in KERNELS}


# Quick access
KERNEL_BY_ID = {k.id: k for k in KERNELS}
KERNEL_BY_NAME = {k.name.lower(): k for k in KERNELS}


# ============================================================================
#                          EXPORTS
# ============================================================================

__all__ = [
    "EthicalKernel",
    "KernelCategory", 
    "KERNELS",
    "KERNEL_BY_ID",
    "KERNEL_BY_NAME",
    "get_kernel_by_id",
    "get_kernel_by_name",
    "get_kernels_by_category",
    "get_all_kernel_ids",
    "get_kernel_names_map",
]
