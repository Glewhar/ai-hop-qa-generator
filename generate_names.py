#!/usr/bin/env python3
"""Generate 100,000 unique full names across a curated multi-cultural mix.

Distribution:
  20% Western, 10% Slavic, 10% African, 20% Asian, 5% Arab, 35% Mixed.
All names use the Latin alphabet (ASCII, romanized where needed).
"""

import random
from pathlib import Path

SEED = 42
OUTPUT = Path(__file__).parent / "names.txt"
TARGET_TOTAL = 100_000
MAX_ATTEMPTS_PER_BUCKET = 10_000_000


# ---------------------------------------------------------------------------
# Name pools
# ---------------------------------------------------------------------------

WESTERN_FIRST = [
    # English (US/UK/Irish)
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
    "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark",
    "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian",
    "George", "Timothy", "Ronald", "Jason", "Edward", "Jeffrey", "Ryan", "Jacob",
    "Nicholas", "Eric", "Jonathan", "Stephen", "Benjamin", "Samuel", "Gregory",
    "Frank", "Alexander", "Raymond", "Patrick", "Jack", "Dennis", "Jerry",
    "Oliver", "Harry", "Henry", "Leo", "Arthur", "Noah", "Ethan", "Mason",
    "Logan", "Lucas", "Owen", "Dylan", "Liam", "Sean", "Connor", "Cian",
    "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan",
    "Jessica", "Sarah", "Karen", "Nancy", "Betty", "Margaret", "Sandra",
    "Ashley", "Kimberly", "Emily", "Donna", "Michelle", "Dorothy", "Carol",
    "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca", "Laura", "Sharon",
    "Cynthia", "Kathleen", "Amy", "Angela", "Helen", "Anna", "Brenda", "Nicole",
    "Emma", "Samantha", "Katherine", "Christine", "Olivia", "Charlotte", "Sophia",
    "Isabella", "Ava", "Mia", "Amelia", "Harper", "Evelyn", "Abigail", "Grace",
    # German / Austrian
    "Hans", "Klaus", "Peter", "Wolfgang", "Karl", "Walter", "Horst", "Dieter",
    "Manfred", "Helmut", "Gerhard", "Werner", "Heinz", "Kurt", "Friedrich",
    "Otto", "Stefan", "Andreas", "Uwe", "Lars", "Matthias", "Tobias", "Sebastian",
    "Ursula", "Helga", "Ingrid", "Renate", "Monika", "Petra", "Sabine", "Andrea",
    "Susanne", "Claudia", "Heike", "Birgit", "Gisela",
    # French
    "Pierre", "Jean", "Michel", "Philippe", "Alain", "Bernard", "Henri", "Jacques",
    "Louis", "Claude", "Nicolas", "Laurent", "Thierry", "Christophe", "Julien",
    "Antoine", "Olivier", "Sebastien", "Vincent", "Francois", "Gilles", "Guillaume",
    "Marie", "Francoise", "Monique", "Isabelle", "Sylvie", "Nathalie", "Martine",
    "Valerie", "Brigitte", "Dominique", "Sophie", "Camille", "Celine", "Corinne",
    # Italian
    "Giovanni", "Giuseppe", "Marco", "Francesco", "Luca", "Paolo", "Roberto",
    "Matteo", "Davide", "Lorenzo", "Alessandro", "Stefano", "Salvatore",
    "Giulia", "Francesca", "Chiara", "Martina", "Alessia", "Elena", "Valentina",
    "Federica", "Paola", "Silvia", "Daniela",
    # Spanish / Portuguese
    "Jose", "Juan", "Carlos", "Luis", "Manuel", "Jorge", "Javier", "Miguel",
    "Pedro", "Alejandro", "Fernando", "Diego", "Rafael", "Ricardo", "Sergio",
    "Pablo", "Andres", "Joaquim", "Rodrigo", "Tiago",
    "Carmen", "Isabel", "Rosa", "Pilar", "Cristina", "Marta", "Lucia", "Paula",
    "Sofia", "Beatriz", "Ines",
    # Scandinavian
    "Erik", "Sven", "Nils", "Anders", "Magnus", "Johan", "Henrik", "Mikael",
    "Per", "Mats", "Bjorn", "Ragnar", "Gunnar",
    "Elin", "Karin", "Eva", "Helena", "Linnea", "Astrid", "Sigrid", "Ingeborg",
    # Dutch / Flemish
    "Pieter", "Hendrik", "Willem", "Cornelis", "Bram", "Daan", "Sem", "Niels",
    "Joris", "Maarten",
    "Tess", "Lotte", "Saar", "Floor", "Anouk", "Marieke",
]

WESTERN_LAST = [
    # English
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis",
    "Wilson", "Anderson", "Taylor", "Moore", "Jackson", "Martin", "Lee",
    "Thompson", "White", "Harris", "Clark", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Hill", "Green", "Adams",
    "Nelson", "Baker", "Hall", "Campbell", "Mitchell", "Carter", "Roberts",
    "Phillips", "Evans", "Turner", "Parker", "Edwards", "Collins", "Stewart",
    "Morris", "Murphy", "Cook", "Rogers", "Morgan", "Cooper", "Peterson",
    "Bailey", "Reed", "Kelly", "Howard", "Cox", "Ward", "Richardson",
    "Watson", "Brooks", "Wood", "James", "Bennett", "Gray", "Hughes", "Price",
    "Sanders", "Bell", "Russell", "Powell", "Long", "Foster", "Barnes",
    "Fisher", "Henderson", "Coleman", "Simmons", "Patterson", "Jordan",
    "Reynolds", "Hamilton", "Graham", "Kennedy", "Stone", "Webb", "Tucker",
    "Porter", "Hunter", "Hicks", "Crawford", "Henry", "Boyd", "Mason",
    "Morales", "Kennedy", "Warren", "Dixon", "Ramos", "Reyes", "Burns",
    # German
    "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker",
    "Schulz", "Hoffmann", "Koch", "Bauer", "Richter", "Klein", "Wolf",
    "Neumann", "Schwarz", "Zimmermann", "Braun", "Hofmann", "Hartmann",
    "Lange", "Krause", "Lehmann", "Werner", "Schmitt", "Muller", "Schaefer",
    "Schroeder", "Krueger", "Vogel", "Friedrich", "Keller", "Jung", "Winkler",
    # French
    "Dubois", "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre",
    "Bertrand", "Roux", "Fournier", "Morel", "Girard", "Andre", "Lefevre",
    "Mercier", "Dupont", "Lambert", "Bonnet", "Francois", "Rousseau", "Garnier",
    "Marchand", "Chevalier", "Perrin",
    # Italian
    "Rossi", "Russo", "Ferrari", "Esposito", "Bianchi", "Romano", "Colombo",
    "Ricci", "Marino", "Greco", "Bruno", "Gallo", "Conti", "Mancini",
    "Costa", "Giordano", "Rizzo", "Lombardi", "Moretti", "Barbieri", "Mariani",
    # Spanish / Portuguese
    "Garcia", "Rodriguez", "Gonzalez", "Fernandez", "Lopez", "Martinez",
    "Sanchez", "Perez", "Gomez", "Jimenez", "Ruiz", "Hernandez", "Diaz",
    "Moreno", "Munoz", "Alvarez", "Romero", "Alonso", "Gutierrez", "Navarro",
    "Torres", "Dominguez", "Vazquez", "Ramos", "Silva", "Pereira", "Oliveira",
    "Costa", "Carvalho", "Ferreira", "Almeida", "Rocha",
    # Scandinavian
    "Andersson", "Johansson", "Karlsson", "Nilsson", "Eriksson", "Larsson",
    "Olsson", "Persson", "Svensson", "Gustafsson", "Pettersson", "Jonsson",
    "Jansson", "Hansson", "Bengtsson", "Lindberg", "Lindstrom", "Lundgren",
    "Hansen", "Nielsen", "Pedersen", "Andersen", "Christensen", "Larsen",
    "Sorensen", "Rasmussen", "Jorgensen", "Petersen", "Kristiansen", "Berg",
    # Dutch
    "de Jong", "Jansen", "de Vries", "van den Berg", "van Dijk", "Bakker",
    "Janssen", "Visser", "Smit", "Meijer", "de Boer", "Mulder", "de Groot",
    "Bos", "Vos", "Peters", "Hendriks", "Dekker", "Brouwer", "van Leeuwen",
]

SLAVIC_FIRST = [
    # Russian
    "Aleksandr", "Sergey", "Dmitry", "Andrey", "Alexei", "Maxim", "Evgeniy",
    "Ivan", "Mikhail", "Nikolai", "Pavel", "Vladimir", "Vitaly", "Oleg",
    "Igor", "Konstantin", "Yuri", "Anton", "Boris", "Viktor", "Leonid",
    "Grigory", "Stanislav", "Ruslan", "Arkady", "Vadim", "Roman", "Denis",
    "Artem", "Kirill", "Timur",
    "Olga", "Tatiana", "Svetlana", "Irina", "Natalia", "Ekaterina", "Yulia",
    "Ludmila", "Nadezhda", "Galina", "Larisa", "Valentina", "Vera", "Polina",
    "Anastasia", "Daria", "Sofya", "Alina", "Marina", "Yelena", "Zoya",
    # Polish
    "Piotr", "Krzysztof", "Andrzej", "Stanislaw", "Tomasz", "Pawel", "Marek",
    "Michal", "Grzegorz", "Jerzy", "Tadeusz", "Jakub", "Lukasz", "Wojciech",
    "Mateusz", "Dawid", "Kazimierz", "Rafal", "Robert",
    "Katarzyna", "Malgorzata", "Agnieszka", "Krystyna", "Elzbieta", "Zofia",
    "Teresa", "Magdalena", "Joanna", "Dorota", "Halina",
    # Ukrainian
    "Taras", "Oleksandr", "Volodymyr", "Mykola", "Vasyl", "Bohdan", "Serhii",
    "Andrii", "Dmytro", "Petro", "Stepan", "Ostap", "Yaroslav", "Danylo",
    "Oksana", "Lesya", "Olha", "Iryna", "Kateryna", "Halyna", "Svitlana",
    "Tetiana", "Mariya",
    # Czech / Slovak
    "Jiri", "Jaroslav", "Miroslav", "Frantisek", "Zdenek", "Milan", "Vaclav",
    "Karel", "Lukas", "Vit", "Radek", "Martin", "Jindrich",
    "Jana", "Hana", "Alena", "Lenka", "Katerina", "Lucie", "Zuzana", "Marketa",
    "Eliska",
    # Serbian / Croatian / Bosnian
    "Marko", "Nikola", "Aleksandar", "Dusan", "Luka", "Vuk", "Dragan", "Milos",
    "Goran", "Djordje", "Zoran", "Stefan", "Filip",
    "Jelena", "Marija", "Ivana", "Milica", "Jovana", "Tijana", "Dragana", "Sanja",
    "Katarina",
    # Bulgarian
    "Georgi", "Dimitar", "Stoyan", "Hristo", "Borislav", "Krasimir",
    "Ivanka", "Petya", "Rositsa", "Desislava", "Gergana", "Tsvetanka",
]

SLAVIC_LAST = [
    # Russian
    "Ivanov", "Smirnov", "Kuznetsov", "Popov", "Vasiliev", "Petrov", "Sokolov",
    "Mikhailov", "Novikov", "Fedorov", "Morozov", "Volkov", "Alekseev",
    "Lebedev", "Semenov", "Egorov", "Pavlov", "Kozlov", "Stepanov", "Nikolaev",
    "Orlov", "Andreev", "Makarov", "Nikitin", "Zakharov", "Zaitsev", "Solovyov",
    "Borisov", "Yakovlev", "Grigoriev", "Romanov", "Vorobyov", "Kiselyov",
    "Ilyin", "Maksimov", "Vinogradov", "Belov", "Komarov", "Antonov",
    # Polish
    "Nowak", "Kowalski", "Wisniewski", "Wojcik", "Kowalczyk", "Kaminski",
    "Lewandowski", "Zielinski", "Szymanski", "Wozniak", "Dabrowski",
    "Kozlowski", "Jankowski", "Mazur", "Kwiatkowski", "Krawczyk", "Kaczmarek",
    "Piotrowski", "Grabowski", "Zajac", "Pawlowski", "Michalski", "Krol",
    "Adamczyk", "Dudek", "Nowakowski", "Baran", "Maciejewski", "Sikora",
    "Kubiak", "Stepien", "Wieczorek",
    # Ukrainian
    "Melnyk", "Shevchenko", "Boyko", "Kovalenko", "Bondarenko", "Tkachenko",
    "Kovalchuk", "Kravchenko", "Oliynyk", "Shevchuk", "Polishchuk", "Bondar",
    "Tkachuk", "Marchenko", "Moroz", "Lysenko", "Rudenko", "Savchenko",
    "Koval", "Mykhailenko", "Kravchuk", "Kozachenko",
    # Czech / Slovak
    "Novak", "Svoboda", "Novotny", "Dvorak", "Cerny", "Prochazka", "Kucera",
    "Vesely", "Horak", "Nemec", "Pokorny", "Pospisil", "Hajek", "Jelinek",
    "Kral", "Ruzicka", "Benes", "Fiala", "Sedlacek", "Dolezal", "Marek",
    "Stastny", "Kratky", "Krejci", "Urban", "Havel",
    # Serbian / Croatian
    "Jovanovic", "Petrovic", "Nikolic", "Markovic", "Djordjevic", "Stojanovic",
    "Ilic", "Pavlovic", "Milosevic", "Popovic", "Jankovic", "Kovacevic",
    "Mitrovic", "Vasic", "Todorovic", "Simic", "Maksimovic", "Horvat",
    "Kovac", "Babic", "Lukic",
    # Bulgarian
    "Georgiev", "Dimitrov", "Stoyanov", "Hristov", "Todorov", "Marinov",
    "Angelov", "Kolev", "Dimov", "Iliev", "Kostov", "Petkov", "Mihaylov",
    "Atanasov", "Vasilev", "Mladenov",
]

AFRICAN_FIRST = [
    # Nigerian (Yoruba / Igbo / Hausa)
    "Chinedu", "Chidi", "Emeka", "Obi", "Ifeanyi", "Ngozi", "Chinyere",
    "Adaeze", "Oluwaseun", "Oluwatobi", "Adebayo", "Olumide", "Ayodeji",
    "Tunde", "Femi", "Segun", "Biodun", "Babatunde", "Folake", "Omolara",
    "Funke", "Yemi", "Bola", "Abubakar", "Ibrahim", "Musa", "Sani", "Umar",
    "Usman", "Chukwuma", "Obinna", "Nnamdi", "Ikenna",
    "Aisha", "Fatima", "Zainab", "Hauwa", "Halima", "Kemi", "Tolu", "Dayo",
    "Chioma", "Amaka", "Nneka", "Ifunanya",
    # Ethiopian / Eritrean
    "Abebe", "Alemu", "Bekele", "Dawit", "Girma", "Haile", "Mulugeta",
    "Solomon", "Teshome", "Tesfaye", "Yohannes", "Kebede", "Tadesse",
    "Desta", "Fitsum", "Berhanu",
    "Tigist", "Selam", "Hiwot", "Aster", "Meseret", "Almaz", "Mulu",
    "Genet", "Mekdes", "Hirut",
    # Swahili / East African
    "Amani", "Baraka", "Jabari", "Jafari", "Juma", "Kamau", "Nia", "Zuri",
    "Asha", "Amina", "Fatuma", "Zawadi", "Imara", "Shani", "Subira", "Jitu",
    "Rafiki", "Maisha", "Bahati",
    # Ghanaian (Akan)
    "Kwame", "Kofi", "Kwaku", "Yaw", "Kojo", "Kwadwo", "Akosua", "Adwoa",
    "Yaa", "Akua", "Afia", "Ama", "Esi", "Abena", "Nana",
    # Southern African (Zulu, Xhosa, Sotho, Tswana)
    "Sipho", "Thabo", "Mandla", "Bongani", "Zola", "Lunga", "Sizwe", "Themba",
    "Zanele", "Thandi", "Nomvula", "Nobuhle", "Sindiswa", "Lerato", "Palesa",
    "Refiloe", "Tumelo", "Dineo", "Kagiso", "Lindiwe", "Nkosinathi", "Sifiso",
    "Mpho", "Tshepo",
    # Kenyan / Luo
    "Otieno", "Omondi", "Akinyi", "Achieng", "Njeri", "Wanjiru",
]

AFRICAN_LAST = [
    # Nigerian
    "Okafor", "Okonkwo", "Okoye", "Nwosu", "Chukwu", "Adebayo", "Adewale",
    "Adeyemi", "Ogunleye", "Ogundipe", "Afolabi", "Babangida", "Eze",
    "Ibeh", "Onyekachi", "Uche", "Nnaji", "Obasanjo", "Okeke", "Achebe",
    "Balogun", "Olatunji",
    # Ethiopian
    "Abebe", "Alemu", "Bekele", "Haile", "Kebede", "Tadesse", "Tesfaye",
    "Abera", "Demeke", "Desta", "Kassa", "Lemma", "Mengistu", "Wolde",
    "Gebre", "Assefa", "Woldemariam",
    # Ghanaian
    "Mensah", "Owusu", "Boateng", "Asante", "Agyeman", "Darko", "Ofori",
    "Adjei", "Nkrumah", "Appiah", "Gyasi", "Amoah", "Danso", "Opoku", "Osei",
    "Addo", "Acheampong",
    # South African
    "Ndlovu", "Khumalo", "Mokoena", "Dlamini", "Sithole", "Nkosi", "Zulu",
    "Mthembu", "Mhlongo", "Mbeki", "Zuma", "Ramaphosa", "Biko", "Tshabalala",
    "Nkomo", "Mandela", "Tutu", "Molefe", "Masango", "Khoza", "Radebe",
    "Mahlangu", "Ngcobo",
    # East African
    "Mwangi", "Kimani", "Wanjiku", "Kamau", "Njoroge", "Mutua", "Kibet",
    "Kiprotich", "Wanjala", "Onyango",
]

ASIAN_FIRST = [
    # Chinese (Mandarin pinyin)
    "Wei", "Lei", "Ming", "Jing", "Hua", "Hong", "Jun", "Xin", "Yang",
    "Fang", "Feng", "Hao", "Qiang", "Bin", "Xiao", "Ling", "Mei", "Na",
    "Ying", "Yan", "Tao", "Zhen", "Peng", "Tian", "Dan", "Kai", "Long",
    "Zhi", "Rong", "Xue", "Hui", "Qing", "Jie", "Bo", "Chao", "Yong",
    "Ping", "Shan", "Lan", "Yi", "Juan", "Yun", "Min", "Cheng", "Wen",
    "Gang", "Bao", "Fu",
    # Japanese
    "Haruto", "Yuto", "Sota", "Hayato", "Takumi", "Ren", "Riku", "Kaito",
    "Daiki", "Ayumu", "Takeru", "Kenta", "Shota", "Ryo", "Kenji", "Akira",
    "Hiroshi", "Satoshi", "Takeshi", "Yuki", "Haruki", "Sho", "Tatsuya",
    "Naoki", "Kazuki", "Ryota", "Yusuke",
    "Tomoko", "Aiko", "Keiko", "Yumiko", "Emiko", "Noriko", "Miyuki",
    "Sakura", "Yui", "Hina", "Mio", "Rio", "Kaede", "Rin", "Akari",
    "Nanami", "Misaki", "Ayaka", "Kana",
    # Korean (romanized)
    "Minjun", "Seojun", "Doyun", "Jiho", "Jaewon", "Junseo", "Hyunwoo",
    "Yoonho", "Taeyang", "Seunghyun", "Sungmin", "Jaehyun", "Minho",
    "Jisoo", "Woojin", "Hyunsik",
    "Jimin", "Seoyeon", "Haeun", "Minseo", "Jiwoo", "Seoyun", "Eunji",
    "Yujin", "Haewon", "Naeun", "Chaeyoung", "Soojin",
    # South Asian (Indian)
    "Aarav", "Arjun", "Rohan", "Rahul", "Aditya", "Vikram", "Raj", "Ravi",
    "Sanjay", "Amit", "Ankit", "Vivek", "Karan", "Rohit", "Nikhil", "Aryan",
    "Ishaan", "Krishna", "Rajesh", "Sandeep", "Deepak", "Manoj", "Suresh",
    "Ramesh", "Anil", "Prakash", "Vijay", "Ajay", "Ashok", "Sunil",
    "Priya", "Pooja", "Neha", "Riya", "Anjali", "Kavita", "Sunita", "Meera",
    "Radha", "Divya", "Swati", "Shruti", "Aishwarya", "Sneha", "Anita",
    "Geeta", "Lakshmi", "Sita", "Padma", "Nisha", "Deepika", "Ritu",
    # Pakistani / Bangladeshi (overlap with Arab)
    "Imran", "Faisal", "Bilal", "Asad", "Tariq", "Zain", "Farhan", "Kamran",
    "Salman", "Waqar", "Rashid",
    "Sana", "Mariam", "Bushra", "Nadia", "Sadia", "Saba", "Rabia", "Hira",
    # Vietnamese (given names)
    "Minh", "Linh", "Hoa", "Huong", "Trang", "Thuy", "Lan", "Mai", "Phuong",
    "Quang", "Tuan", "Hung", "Dung", "Binh", "Cuong", "Duc", "Nam", "Phong",
    "Son", "Thanh", "Tien", "Tung", "Hieu", "Khanh",
    # Thai
    "Somchai", "Somsak", "Chaiwat", "Kittisak", "Thanakorn", "Suchart",
    "Malee", "Nok", "Pim", "Ploy", "Fern", "Nan", "Bua", "Pui",
    # Indonesian
    "Adi", "Agus", "Bambang", "Budi", "Dedi", "Eko", "Hadi", "Joko", "Rudi",
    "Rizki", "Sari", "Siti", "Dewi", "Rini", "Yanti", "Nurul", "Anisa",
    "Indah", "Ratih",
    # Filipino
    "Emil", "Jomar", "Rey", "Ricky", "Arnel", "Rodel", "Rogelio", "Ernesto",
    "Cristina", "Josefina",
    # Malay
    "Zainal", "Aminah", "Fatimah", "Rosnah", "Noraini",
]

ASIAN_LAST = [
    # Chinese
    "Wang", "Li", "Zhang", "Liu", "Chen", "Yang", "Huang", "Zhao", "Wu",
    "Zhou", "Xu", "Sun", "Ma", "Zhu", "Hu", "Guo", "He", "Gao", "Lin",
    "Luo", "Zheng", "Liang", "Xie", "Song", "Tang", "Han", "Feng", "Deng",
    "Cao", "Peng", "Zeng", "Xiao", "Tian", "Dong", "Yuan", "Shen", "Lu",
    "Jiang", "Cui", "Fan", "Fang",
    # Japanese
    "Sato", "Suzuki", "Takahashi", "Tanaka", "Watanabe", "Ito", "Yamamoto",
    "Nakamura", "Kobayashi", "Kato", "Yoshida", "Yamada", "Sasaki",
    "Yamaguchi", "Matsumoto", "Inoue", "Kimura", "Hayashi", "Shimizu",
    "Yamazaki", "Mori", "Abe", "Ikeda", "Hashimoto", "Yamashita",
    "Ishikawa", "Nakajima", "Maeda", "Fujita", "Ogawa", "Ono", "Okada",
    "Goto",
    # Korean
    "Kim", "Lee", "Park", "Choi", "Jung", "Kang", "Cho", "Yoon", "Jang",
    "Lim", "Han", "Oh", "Seo", "Shin", "Kwon", "Hwang", "Ahn", "Song",
    "Hong", "Yoo", "Baek", "Nam",
    # South Asian
    "Sharma", "Verma", "Patel", "Singh", "Kumar", "Gupta", "Rao", "Reddy",
    "Mehta", "Agarwal", "Jain", "Mishra", "Yadav", "Pandey", "Iyer", "Nair",
    "Menon", "Shah", "Khan", "Ahmed", "Hussain", "Siddiqui", "Qureshi",
    "Chaudhary", "Bhatia", "Kapoor", "Malhotra", "Chopra", "Das", "Ghosh",
    "Banerjee", "Chatterjee", "Mukherjee", "Roy", "Sen", "Bose", "Saha",
    "Chowdhury", "Islam", "Rahman", "Hossain", "Perera", "Fernando",
    "Jayawardena", "Shrestha", "Thapa", "Gurung", "Tamang", "Rai", "Magar",
    "Bhattarai",
    # Southeast Asian
    "Nguyen", "Tran", "Le", "Pham", "Hoang", "Huynh", "Vo", "Vu", "Dang",
    "Bui", "Do", "Ho", "Ngo", "Duong", "Ly", "Dao",
    "Srisuk", "Jaidee", "Thongchai", "Suwan", "Rattanakorn", "Wongsawat",
    "Sittichai", "Chaiyasit",
    "Wijaya", "Kusuma", "Santoso", "Wibowo", "Pranata", "Setiawan", "Halim",
    "Sudirman", "Hakim", "Saputra",
    "Santos", "Reyes", "Cruz", "Bautista", "Aquino", "Villanueva",
    "Marasigan", "Dela Cruz", "Gonzales", "Ramos",
]

ARAB_FIRST = [
    "Ahmed", "Mohammed", "Mahmoud", "Khalid", "Ali", "Hassan", "Hussein",
    "Omar", "Youssef", "Ibrahim", "Mustafa", "Abdullah", "Abdulrahman",
    "Khalil", "Faisal", "Saad", "Waleed", "Karim", "Samir", "Tarek",
    "Nader", "Rashid", "Zaid", "Hamza", "Salem", "Sami", "Marwan", "Fahd",
    "Ahmad", "Yasser", "Bassam", "Jamal", "Kamal", "Majid", "Nabil",
    "Othman", "Qasim", "Ramzi", "Sherif", "Tamer", "Wael", "Ziad", "Adel",
    "Bahaa", "Nasser", "Mazen", "Rami", "Hatem",
    "Fatima", "Aisha", "Maryam", "Noor", "Layla", "Zainab", "Khadija",
    "Hana", "Huda", "Rania", "Amira", "Dalia", "Yasmin", "Leila", "Nadia",
    "Samira", "Sara", "Salma", "Farah", "Reem", "Mona", "Hala", "Iman",
    "Jihan", "Lubna", "Sawsan", "Walaa", "Zeinab", "Nour", "Asma",
]

ARAB_LAST = [
    "Al-Ahmad", "Al-Hassan", "Al-Mansour", "Al-Rashid", "Al-Sayed",
    "Al-Hashimi", "Al-Saud", "Al-Maktoum", "Al-Nahyan", "Al-Thani",
    "Al-Khalifa", "Al-Sabah", "Al-Amin", "Al-Jaber", "Al-Mutairi",
    "Al-Otaibi", "Al-Dosari", "Al-Shammari", "Al-Qahtani", "Al-Ghamdi",
    "Al-Harbi", "Al-Sulaiman", "Al-Farsi", "Al-Zahrani", "Al-Balushi",
    "Al-Khoury", "Al-Najjar", "Al-Masri", "Al-Azhari", "Al-Hariri",
    "Al-Sharif", "Al-Tamimi",
    "Haddad", "Khoury", "Nassar", "Saab", "Awad", "Mansour", "Fayed",
    "Hakim", "Samaha", "Issa", "Karam", "Salib", "Ghanem", "Habib",
    "Jaber", "Khalil", "Malouf", "Najjar", "Rahal", "Saliba", "Zaki",
    "Younis", "Aziz", "Dabbas", "Farah", "Gharib", "Hamdan", "Jarrah",
    "Kassem", "Lababidi", "Masri", "Nasr", "Obeid", "Qasim", "Shadid",
    "Tannous", "Wahba",
]

MIDDLE_WESTERN = [
    "James", "John", "Michael", "David", "William", "Thomas", "Robert",
    "Charles", "Joseph", "Edward", "George", "Henry", "Frederick", "Arthur",
    "Alexander", "Daniel", "Samuel", "Benjamin", "Lee", "Allen", "Scott",
    "Ray", "Wayne", "Dean", "Paul", "Mark", "Neil", "Kyle", "Reid",
    "Marie", "Anne", "Louise", "Rose", "Grace", "Jane", "Elizabeth",
    "Catherine", "May", "Lynn", "Faye", "Mae", "Joy", "Beth", "Claire",
    "Anna", "Sophia", "Isabelle", "Hope", "Belle", "Kate",
    "Wilhelm", "Heinrich", "Franz", "Otto", "Klaus", "Jean", "Philippe",
    "Luigi", "Carlo", "Pablo", "Luis", "Lars", "Olaf", "Henrik", "Anders",
]

MIDDLE_SLAVIC = [
    "Ivanovich", "Petrovich", "Aleksandrovich", "Sergeevich", "Dmitrievich",
    "Nikolaevich", "Mikhailovich", "Vladimirovich", "Andreevich", "Yurievich",
    "Pavlovich", "Viktorovich",
    "Ivanovna", "Petrovna", "Aleksandrovna", "Sergeevna", "Dmitrievna",
    "Nikolaevna", "Mikhailovna", "Vladimirovna", "Andreevna", "Yurievna",
    "Pavlovna", "Viktorovna",
    "Jan", "Adam", "Piotr", "Maria", "Anna", "Josef", "Vaclav", "Marek",
    "Stanislav",
]

MIDDLE_AFRICAN = [
    "Kwame", "Kofi", "Ade", "Chi", "Olu", "Ayo", "Bola", "Tunde", "Sipho",
    "Thabo", "Mandla", "Abebe", "Haile", "Dawit", "Nia", "Amani", "Baraka",
    "Imara", "Zuri", "Ngozi", "Chinedu", "Kwaku", "Yaw", "Adaeze", "Folake",
]

MIDDLE_ASIAN = [
    "Hiro", "Ken", "Taka", "Shin", "Kai", "Ryu", "Jun", "Min", "Ho", "Sung",
    "Kumar", "Prasad", "Nath", "Chandra", "Devi", "Bai", "Raj", "Lal", "Das",
    "Van", "Thi", "Ngoc", "Anh", "Thanh", "Kim", "Duc",
]

MIDDLE_ARAB = [
    "Ahmed", "Mohammed", "Ali", "Hassan", "Omar", "Khalil", "Youssef",
    "Ibrahim", "Abdullah", "Khaled", "Hamza", "Rashid",
    "Fatima", "Aisha", "Layla", "Noor", "Maryam", "Huda", "Rania", "Sara",
    "Salma", "Amira",
]

ARAB_PARTICLES = ["bin", "ibn", "bint"]


POOLS = {
    "western": (WESTERN_FIRST, WESTERN_LAST),
    "slavic":  (SLAVIC_FIRST,  SLAVIC_LAST),
    "african": (AFRICAN_FIRST, AFRICAN_LAST),
    "asian":   (ASIAN_FIRST,   ASIAN_LAST),
    "arab":    (ARAB_FIRST,    ARAB_LAST),
}

ALL_FIRST = (
    WESTERN_FIRST + SLAVIC_FIRST + AFRICAN_FIRST + ASIAN_FIRST + ARAB_FIRST
)
ALL_LAST = (
    WESTERN_LAST + SLAVIC_LAST + AFRICAN_LAST + ASIAN_LAST + ARAB_LAST
)
ALL_MIDDLE = (
    MIDDLE_WESTERN + MIDDLE_SLAVIC + MIDDLE_AFRICAN + MIDDLE_ASIAN + MIDDLE_ARAB
)

POOLS["mixed"] = (ALL_FIRST, ALL_LAST)

MIDDLE_POOLS = {
    "western": MIDDLE_WESTERN,
    "slavic":  MIDDLE_SLAVIC,
    "african": MIDDLE_AFRICAN,
    "asian":   MIDDLE_ASIAN,
    "arab":    MIDDLE_ARAB,
    "mixed":   ALL_MIDDLE,
}

MIDDLE_RATE = {
    "western": 0.40,
    "slavic":  0.40,
    "african": 0.40,
    "asian":   0.15,
    "arab":    0.50,
    "mixed":   0.35,
}

QUOTAS = {
    "western": 20_000,
    "slavic":  10_000,
    "african": 10_000,
    "asian":   20_000,
    "arab":    5_000,
    "mixed":   35_000,
}


def generate_bucket(rng: random.Random, bucket: str, count: int,
                    seen: set) -> list:
    firsts, lasts = POOLS[bucket]
    middles = MIDDLE_POOLS[bucket]
    middle_rate = MIDDLE_RATE[bucket]
    results = []
    attempts = 0
    while len(results) < count:
        attempts += 1
        if attempts > MAX_ATTEMPTS_PER_BUCKET:
            raise RuntimeError(
                f"Could not fill bucket '{bucket}' after {attempts} attempts "
                f"({len(results)}/{count} produced). Pool too small."
            )
        first = rng.choice(firsts)
        last = rng.choice(lasts)
        if rng.random() < middle_rate:
            if bucket == "arab" and rng.random() < 0.5:
                particle = rng.choice(ARAB_PARTICLES)
                middle = rng.choice(middles)
                name = f"{first} {particle} {middle} {last}"
            else:
                middle = rng.choice(middles)
                name = f"{first} {middle} {last}"
        else:
            name = f"{first} {last}"
        if name in seen:
            continue
        seen.add(name)
        results.append(name)
    return results


def main() -> None:
    rng = random.Random(SEED)
    seen: set = set()
    output: list = []
    for bucket, count in QUOTAS.items():
        output.extend(generate_bucket(rng, bucket, count, seen))

    assert sum(QUOTAS.values()) == TARGET_TOTAL
    assert len(output) == TARGET_TOTAL, \
        f"expected {TARGET_TOTAL}, got {len(output)}"
    assert len(seen) == TARGET_TOTAL, \
        f"seen set has {len(seen)}, expected {TARGET_TOTAL}"

    rng.shuffle(output)

    for line in output:
        assert line and line == line.strip() and "  " not in line, \
            f"bad line: {line!r}"

    with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(output) + "\n")

    print(f"Wrote {len(output):,} unique names to {OUTPUT}")


if __name__ == "__main__":
    main()
