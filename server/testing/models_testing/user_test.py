from sqlalchemy.exc import IntegrityError
import pytest

from app import app
from models import db, User, Recipe

class TestUser:
    '''User in models.py'''

    def test_has_attributes(self):
        '''has attributes username, _password_hash, image_url, and bio.'''
        
        with app.app_context():

            User.query.delete()
            db.session.commit()

            user = User(
                username="Liz",
                image_url="https://prod-images.tcm.com/Master-Profile-Images/ElizabethTaylor.jpg",
                bio="""Dame Elizabeth Rosemond Taylor DBE (February 27, 1932""" + \
                    """ - March 23, 2011) was a British-American actress. """ + \
                    """She began her career as a child actress in the early""" + \
                    """ 1940s and was one of the most popular stars of """ + \
                    """classical Hollywood cinema in the 1950s. She then""" + \
                    """ became the world's highest paid movie star in the """ + \
                    """1960s, remaining a well-known public figure for the """ + \
                    """rest of her life. In 1999, the American Film Institute""" + \
                    """ named her the seventh-greatest female screen legend """ + \
                    """of Classic Hollywood cinema."""
            )

            user.password_hash = "whosafraidofvirginiawoolf"
            
            db.session.add(user)
            db.session.commit()

            created_user = User.query.filter(User.username == "Liz").first()

            assert(created_user.username == "Liz")
            assert(created_user.image_url == "https://prod-images.tcm.com/Master-Profile-Images/ElizabethTaylor.jpg")
            assert(created_user.bio == \
                """Dame Elizabeth Rosemond Taylor DBE (February 27, 1932""" + \
                """ - March 23, 2011) was a British-American actress. """ + \
                """She began her career as a child actress in the early""" + \
                """ 1940s and was one of the most popular stars of """ + \
                """classical Hollywood cinema in the 1950s. She then""" + \
                """ became the world's highest paid movie star in the """ + \
                """1960s, remaining a well-known public figure for the """ + \
                """rest of her life. In 1999, the American Film Institute""" + \
                """ named her the seventh-greatest female screen legend """ + \
                """of Classic Hollywood cinema.""")
            
            with pytest.raises(AttributeError):
                created_user.password_hash

    def test_requires_username(self):
        '''requires each record to have a username.'''

        with app.app_context():

            User.query.delete()
            db.session.commit()

            user = User()
            with pytest.raises(IntegrityError):
                db.session.add(user)
                db.session.commit()

    def test_requires_unique_username(self):
        '''requires each record to have a username.'''

        with app.app_context():

            User.query.delete()
            db.session.commit()

            user_1 = User(username="Ben")
            user_2 = User(username="Ben")

            with pytest.raises(IntegrityError):
                db.session.add_all([user_1, user_2])
                db.session.commit()

    def test_has_list_of_recipes(self):
        '''has records with lists of recipes records attached.'''

        with app.app_context():

            User.query.delete()
            Recipe.query.delete()
            db.session.commit()

            user = User(username="Prabhdip")
            user.password_hash = "password"  # FIX 1

            recipe_1 = Recipe(
                title="Delicious Shed Ham",
                instructions="""Or kind rest bred with am shed then. In""" + \
                    """ raptures building an bringing be. Elderly is detract""" + \
                    """ tedious assured private so to visited. Do travelling""" + \
                    """ companions contrasted it. Mistress strongly remember""" + \
                    """ up to. Ham him compass you proceed calling detract.""" + \
                    """ Better of always missed we person mr. September""" + \
                    """ smallness northward situation few her certainty""" + \
                    """ something.""",
                minutes_to_complete=60,
            )
            recipe_2 = Recipe(
                title="Hasty Party Ham",
                instructions="""As am hastily invited settled at limited""" + \
                             """ civilly fortune me. Really spring in extent""" + \
                             """ an by. Judge but built gay party world. Of""" + \
                             """ so am he remember although required. Bachelor""" + \
                             """ unpacked be advanced at. Confined in declared""" + \
                             """ marianne is vicinity.""",
                minutes_to_complete=30,
            )

            user.recipes.append(recipe_1)
            user.recipes.append(recipe_2)

            db.session.add_all([user, recipe_1, recipe_2])
            db.session.commit()

            # check that all were created in db
            assert(user.id)
            assert(recipe_1.id)
            assert(recipe_2.id)

            # check that recipes were saved to user
            assert(recipe_1 in user.recipes)
            assert(recipe_2 in user.recipes)

    def test_user_password_hash(self):
        '''tests setting and committing a password hash.'''

        with app.app_context():

            User.query.delete()
            Recipe.query.delete()
            db.session.commit()

            user = User(username="TestUser2")  # FIX 3: use unique username
            user.password_hash = "password"  # This sets _password_hash
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                title="Some title",
                instructions="A" * 60,  # FIX 2: at least 50 chars
                minutes_to_complete=10,
                user_id=user.id  # or user=user
            )
            db.session.add(recipe)
            db.session.commit()

def test_user_creation():
    with app.app_context():
        User.query.delete()
        db.session.commit()
        user = User(username="TestUser3")  # FIX 3: use unique username
        user.password_hash = "password"
        db.session.add(user)
        db.session.commit()
        assert user.id is not None

def test_user_with_recipe():
    with app.app_context():
        Recipe.query.delete()
        User.query.delete()
        db.session.commit()

        user = User(username="TestUser4")  # FIX 3: use unique username
        user.password_hash = "password"
        db.session.add(user)
        db.session.commit()

        recipe = Recipe(
            title="Test Recipe",
            instructions="This is a long enough instructions string for the test. It is definitely more than fifty characters.",
            minutes_to_complete=10,
            user_id=user.id
        )
        db.session.add(recipe)
        db.session.commit()

        assert recipe.user_id == user.id