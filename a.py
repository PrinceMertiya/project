from nodue import app, db, User

# Replace 'nodue' with the actual name of your Flask app module

with app.app_context():
    # Uncomment this part if you want to create 'user1'
    '''
    user1 = User(
        username='new',
        password='123456',
        role='Student',
        college_name='Example College',
        branch_name='Computer Science'
    )
    db.session.add(user1)
    '''

    # Create 'user2'
    user5= User(
        username='prime',
        password='123456',
        role='Admin',
        college_name='xyz College',
        branch_name='Computer Science'
    )
    db.session.add(user5)

    db.session.commit()

    print("Users added successfully.")
