db.createUser({
	user: process.env.QUARKUS_MONGODB_CREDENTIALS_USERNAME,
	pwd: process.env.QUARKUS_MONGODB_CREDENTIALS_PASSWORD,
	roles: [{
		role: 'readWrite',
		db: process.env.QUARKUS_MONGODB_DATABASE
	}]
})
