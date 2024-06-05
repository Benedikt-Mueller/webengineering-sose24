class Choices:
    def __str__():
        return "This Class contains all Choices for choice fields"
    
    PREFERENCE_CHOICES = (
        ('international' , 'Internationale Küche'),
        ('german' , 'Deutsche Küche'),
        ('danish' , 'Dänische Küche'),
        ('italian' , 'Italienische Küche'),
        ('american' , 'Amerikanische Küche'),
        ('indian' , 'Indische Küche'),
        ('asian' , 'Asiatische Küche'),
    )

    VOTE_CHOICES = (
        ('one_star', '1/5'),
        ('two_star', '2/5'),
        ('three_star', '3/5'),
        ('four_star', '4/5'),
        ('five_star', '5/5'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )

    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('owner', 'Restaurant Owner'),
        ('staff', 'Restaurant Staff'),
        ('admin', 'System Administrator'),
        ('developer', 'Developer'),
        ('marketing', 'Marketing Team Member'),
    )
