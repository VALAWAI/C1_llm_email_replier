db.createUser({
	user: process.env.DB_USER_NAME,
	pwd: process.env.DB_USER_PASSWORD,
	roles: [{
		role: 'readWrite',
		db: process.env.DB_NAME
	}]
})
