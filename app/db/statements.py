from sqlalchemy import text

insert_user_with_email = text(f"""
    INSERT INTO auth.users (
        name,
        email,
        password,
        type,
        status
    ) VALUES (
        :name,
        :email,
        crypt(:password, gen_salt('md5')),
        :type,
        :status
    ) RETURNING id;
""")

insert_user_with_social_credentials = text(f"""
    INSERT INTO auth.users (
        name,
        email,
        type,
        status
    ) VALUES (
        :name,
        :email,
        :type,
        :status
    ) RETURNING id;
""")