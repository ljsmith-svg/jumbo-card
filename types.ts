
export enum CharacterTheme {
  // Sesame Street
  ELMO = 'Elmo (Sesame Street)',
  COOKIE_MONSTER = 'Cookie Monster (Sesame Street)',
  BIG_BIRD = 'Big Bird (Sesame Street)',
  ABBY = 'Abby Cadabby (Sesame Street)',
  GROVER = 'Grover (Sesame Street)',
  OSCAR = 'Oscar the Grouch (Sesame Street)',
  BERT_ERNIE = 'Bert & Ernie (Sesame Street)',

  STITCH = 'Stitch (Cute + Christmas Outfit)',
  SPIDERMAN = 'Spider-Man (Cartoon Style)',
  
  // Princesses
  ELSA = 'Princess Elsa (Cartoon)',
  ANNA = 'Princess Anna Inspired (Frozen)',
  SNOW_WHITE = 'Snow White Inspired (Cartoon)',
  CINDERELLA = 'Cinderella Inspired (Cartoon)',
  AURORA = 'Princess Aurora Inspired (Sleeping Beauty)',
  ARIEL = 'Princess Ariel Inspired (Little Mermaid)',
  BELLE = 'Princess Belle Inspired (Beauty & Beast)',
  JASMINE = 'Princess Jasmine Inspired (Aladdin)',
  POCAHONTAS = 'Pocahontas Inspired (Cartoon)',
  MULAN = 'Mulan Inspired (Cartoon)',
  TIANA = 'Princess Tiana Inspired (Princess & Frog)',
  RAPUNZEL = 'Rapunzel Inspired (Tangled)',
  MERIDA = 'Merida Inspired (Brave)',
  MOANA = 'Moana Inspired (Cartoon)',
  RAYA = 'Raya Inspired (Dragon Warrior)',
  
  SUPERHERO_GIRL = 'Superhero Girl (Generic)',
  SUPERHERO_BOY = 'Superhero Boy (Generic)',
  MINNIE = 'Minnie Mouse Inspired',
  MICKEY = 'Mickey Mouse Inspired',
  BLUEY = 'Bluey Inspired',
  ROBLOX_BOY = 'Roblox Boy',
  ROBLOX_GIRL = 'Roblox Girl',
  REINDEER_CHIBI = 'Christmas Reindeer Chibi',
  PENGUIN_CHIBI = 'Christmas Penguin Chibi',
  ELF_CHIBI = 'Christmas Elf Chibi',
  SANTA_CHIBI = 'Santa Claus Chibi',
  GINGERBREAD_MAN = 'Gingerbread Man Chibi',
  SNOWMAN_CHIBI = 'Snowman Chibi',
  PUPPY = 'Cute Christmas Puppy',
  KITTEN = 'Cute Christmas Kitten',
  UNICORN = 'Unicorn Christmas',
  DINOSAUR = 'Dinosaur Christmas',
  CANDY_BEAR = 'Candy Bear',
  BABY_YODA = 'Baby Yoda Inspired',
  MARIO = 'Mario Inspired',
  LUIGI = 'Luigi Inspired',
  SONIC = 'Sonic Inspired',
  PAW_PATROL = 'Paw Patrol Inspired',
  LOL_DOLL = 'LOL Doll Inspired',
  BRATZ_DOLL = 'Bratz Doll Inspired (Kid Safe)',
  BARBIE = 'Barbie Inspired',
  BARBIE_AA = 'African American Barbie Inspired',
  RAINBOW_FAIRY = 'Rainbow Fairy',
  ANGEL = 'Christmas Angel',
  MERMAID = 'Holiday Mermaid',
}

export enum CardStyle {
  CARTOON = 'Cartoon',
  CHIBI = 'Chibi',
  GLITTER_BORDER = 'Glitter Border',
  CANDY_CANE_BORDER = 'Candy Cane Border',
}

export enum CardSize {
  SIZE_8_5_11 = '8.5x11',
  SIZE_11_17 = '11x17',
  SIZE_13_19 = '13x19',
}

export enum ColorTheme {
  RED_GREEN = 'Red & Green',
  PINK_CHRISTMAS = 'Pink Christmas',
  BLUE_SNOWFLAKE = 'Blue Snowflake',
  GOLD_WHITE = 'Gold & White',
  PURPLE_SILVER = 'Purple & Silver',
  BLUE_SILVER = 'Blue & Silver',
  CLASSIC_VINTAGE = 'Classic Vintage (Sepia/Red)',
  RAINBOW = 'Rainbow Festive',
  BLACK_GOLD = 'Black & Gold',
  ROSE_GOLD = 'Rose Gold & Blush',
  FROSTY_TEAL = 'Frosty Teal & White',
  CANDY_PASTEL = 'Candy Pastel',
}

export interface CardFormData {
  childName: string;
  toName: string;
  fromName: string;
  characterTheme: CharacterTheme;
  cardStyle: CardStyle;
  cardSize: CardSize;
  colorTheme: ColorTheme;
}

export interface GeneratedImage {
  url: string;
  prompt: string;
}
