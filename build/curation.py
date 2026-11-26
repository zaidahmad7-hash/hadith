"""Hand-picked HadeethEnc ids for the two guided paths. Text always comes from the source, never from here."""

# Start here: 40 essential hadith, all Sahih and narrated by Bukhari and/or Muslim.
START = [
    # Foundations
    '4560',   # Actions are by intentions
    '4563',   # Jibril: Islam, Iman, Ihsan
    '65000',  # Islam is built on five
    '4792',   # Whoever introduces into this matter of ours...
    '4314',   # The lawful is clear and the unlawful is clear
    '4309',   # Religion is sincerity
    '4725',   # Avoid what I have forbidden you
    '4316',   # Allah is good and accepts only what is good
    # Worship
    '4968',   # The five prayers are like a river
    '3365',   # Which deed is dearest to Allah?
    '4196',   # Whoever fasts Ramadan out of faith
    '65004',  # Purity is half of faith
    '5507',   # Two words light on the tongue
    '10412',  # Our Lord descends in the last third of the night
    '5913',   # The best of you learn the Qur'an and teach it
    # Character
    '4717',   # Love for your brother what you love for yourself
    '5437',   # Say what is good or keep silent
    '4709',   # Do not get angry
    '5351',   # The strong man controls himself when angry
    '5803',   # The best of you have the best manners
    '4308',   # Righteousness is good character
    '5504',   # Adhere to truthfulness
    '4319',   # Allah has enjoined excellence in all things
    '5797',   # Allah is gentle and loves gentleness
    '5866',   # Make things easy, not difficult
    '10101',  # A Muslim is one from whose tongue and hand others are safe
    '4969',   # The believers are like one body
    '4706',   # Do not envy one another
    '3361',   # Love one another; spread the greeting of peace
    '5808',   # Feeding people and greeting everyone
    '5348',   # Do not belittle any good deed, even a cheerful face
    '4965',   # Jibril kept enjoining good treatment of the neighbour
    '5440',   # Whoever does not show mercy will not be shown mercy
    # The heart and the Hereafter
    '4555',   # Allah looks at your hearts and deeds
    '4801',   # Whoever relieves a believer of hardship
    '5354',   # Whoever guides to good gets the same reward
    '65001',  # Whoever sees an evil, let him change it
    '4704',   # Be in this world like a stranger or a traveller
    '5449',   # Two blessings: health and free time
    '65566',  # When a person dies, three things continue
]

# Little Learners: short, gentle hadith about everyday manners, for children.
KIDS = [
    '58120',  # Say Bismillah, eat with your right hand
    '5348',   # A cheerful face is a good deed
    '5659',   # He greeted the children with salam
    '3361',   # Spread salam, love one another
    '5504',   # Always tell the truth
    '4717',   # Love for your brother what you love for yourself
    '5437',   # Say good or stay quiet
    '4709',   # Do not get angry
    '5351',   # The truly strong person controls anger
    '5803',   # Best manners
    '4939',   # Gentleness brings goodness
    '5478',   # Modesty is part of faith
    '3433',   # When you sneeze, say Alhamdulillah
    '5280',   # Cover your mouth when you yawn
    '4965',   # Be good to your neighbour
    '4250',   # Give gifts to the nearest neighbour
    '5336',   # Share your food with neighbours
    '6469',   # Removing a thorny branch from the road
    '5350',   # Make room for others
    '3599',   # The giving hand is better
    '5507',   # Two words light on the tongue
    '5913',   # Learn the Qur'an and teach it
    '4555',   # Allah looks at your heart
    '4251',   # Mercy to children
]


# Imam an-Nawawi's 40 Hadith (42 with his additions), in his order. Matched to HadeethEnc by Arabic text.
NAWAWI = ["66511", "4563", "66512", "66513", "66514", "66515", "66516", "4211", "66517", "66518", "66519", "65255", "66520", "4714", "5437", "4709", "66521", "4302", "66522", "66523", "66524", "66525", "66526", "4810", "4558", "66527", "66540", "66529", "66530", "66510", "4307", "66531", "66532", "65001", "4706", "4801", "66533", "66534", "4216", "4704", "66535", "5456"]

# Hadith Qudsi: hadith in which the Prophet ﷺ reports the words of Allah. Selected from HadeethEnc by
# Arabic markers (e.g. "قال الله تعالى", "فيما يرويه عن ربه") and the 40 Hadith Qudsi collection, then reviewed.
QUDSI = ["4810", "3636", "4322", "6461", "6337", "3546", "5805", "10404", "65099", "5456", "4817", "3342", "6327", "66284", "66163", "2981", "3162", "3369", "3362", "3508", "5522", "5544", "6458", "8284", "8272", "8314", "3415", "3707", "4232", "8899", "8343", "8344", "8315", "3261", "8313", "10405", "65010", "5457"]
