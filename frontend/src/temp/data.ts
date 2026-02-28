export const TEMP_CONVERSION: { role: "HUMAN" | "AI"; text: string }[] = [
	{
		role: "HUMAN",
		text: "tell me about the PDF",
	},
	{
		role: "AI",
		text: "this is pdf about alksadadkhsakjdhashdjhahdhsadhsadksajdkjaskdjaskdjasdjkjdasdashdhasdhjashd",
	},
	{
		role: "HUMAN",
		text: "could you explain in 1000 words ",
	},
	// 	{
	// 		role: "AI",
	// 		text: `Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi posuere orci eget tellus malesuada, sed tempus enim eleifend. Maecenas eget auctor leo, in dapibus nisl. Vestibulum ultricies nisl at ex auctor, sit amet congue nunc tempus. Vivamus non ante rhoncus, fringilla turpis quis, auctor odio. Aliquam mi magna, porta id porta at, vulputate iaculis arcu. Mauris faucibus risus mauris, eget semper nunc maximus in. Suspendisse consequat ligula pellentesque purus ornare sagittis. Mauris at mattis dolor. Aliquam nec mattis nisl.

	// Mauris eget hendrerit erat, vitae ultricies tellus. In sodales ultrices odio vel efficitur. Praesent vel dui vel tellus scelerisque feugiat vitae sit amet quam. Aenean a egestas arcu, ac pharetra risus. Nulla facilisi. Etiam gravida lacus sit amet urna mattis semper. Sed tempus dapibus velit ut rutrum. Cras pellentesque rutrum justo eget pharetra. Quisque posuere magna vitae est volutpat posuere.

	// Vestibulum aliquam pharetra justo sit amet mollis. Praesent vitae eros ligula. Nunc rutrum lacinia cursus. Proin accumsan tincidunt gravida. Fusce ut felis at enim aliquet hendrerit et eget lorem. Donec commodo finibus felis at imperdiet. Aliquam erat volutpat. Sed a vulputate quam. Aliquam tortor mi, bibendum a suscipit id, mattis quis justo. Sed suscipit, metus ac luctus posuere, metus ipsum porta arcu, eget egestas massa lacus sit amet tellus. Duis in erat dui. Morbi eget egestas dui. Nullam at eros sodales, ornare sem non, porta sem. Nunc laoreet laoreet laoreet. Duis odio magna, iaculis id enim nec, accumsan semper dui.

	// Ut egestas rhoncus nunc et tempus. Maecenas commodo tempor accumsan. Vestibulum massa ex, imperdiet in ante non, porta vestibulum felis. Proin semper et mauris ut fermentum. In bibendum diam nunc, eget tempor ipsum ornare sit amet. Morbi accumsan risus ac magna posuere, quis auctor purus feugiat. Vestibulum tincidunt, mauris id laoreet consectetur, lacus augue lacinia diam, sit amet tincidunt lacus augue id nisl. Mauris scelerisque magna quis nisl auctor scelerisque.

	// Aenean imperdiet, est eu bibendum venenatis, ipsum tortor auctor lectus, id blandit tortor nunc sollicitudin tellus. Ut tellus ex, ultricies a nulla non, vehicula suscipit ante. Fusce ac porta orci. Proin euismod diam vel risus eleifend varius. Praesent tincidunt lectus nulla, at efficitur nunc luctus vel. Suspendisse eget ante blandit, accumsan tellus in, vehicula nunc. Sed a leo nibh. Nullam eu malesuada lorem. Mauris eget faucibus mi. Integer vitae euismod mi. Sed efficitur, ex non vehicula interdum, mi diam volutpat est, interdum auctor lacus arcu id risus. Praesent vehicula sem ut augue pretium euismod. Aliquam fringilla felis faucibus, sagittis erat a, suscipit ante. Morbi felis elit, elementum eu lorem eget, ornare varius ipsum. Mauris maximus blandit malesuada. Aliquam erat volutpat.

	// Suspendisse mi odio, fermentum vitae est vitae, condimentum congue elit. Aliquam sagittis tortor in neque fringilla, quis cursus lorem faucibus. Sed tincidunt, orci vel luctus hendrerit, elit sapien auctor leo, blandit tempus mauris metus at metus. Pellentesque ut orci vehicula eros finibus tristique. Praesent blandit egestas vestibulum. Suspendisse tristique, risus et eleifend tristique, nibh arcu varius urna, at iaculis velit augue nec lacus. Vivamus pretium justo enim, molestie maximus leo dapibus fringilla. Phasellus volutpat dolor ut placerat aliquam. Suspendisse id nisl sem. Etiam et dui enim. Vestibulum posuere viverra ex vitae sagittis. Fusce tristique, nunc sit amet malesuada fringilla, leo diam pretium sapien, quis semper magna tellus ut justo. Donec non neque lorem. In hac habitasse platea dictumst. Ut auctor nulla vitae tincidunt blandit.

	// Maecenas sed euismod ligula. Etiam quis vulputate lacus, in consectetur urna. In aliquet ultricies lacinia. Nunc gravida libero non finibus molestie. Integer mauris enim, efficitur eu lacus nec, tincidunt luctus nibh. Sed eleifend venenatis massa quis efficitur. Vivamus est dui, ultrices in felis et, commodo rhoncus augue. Vivamus quis quam ac tellus lobortis fermentum ac eget ante. Nam luctus libero vel commodo consequat. Quisque id posuere augue. Vestibulum fringilla at neque eu sagittis. Quisque ac tortor et mi vestibulum auctor id vitae mi. Curabitur justo libero, volutpat in pellentesque vel, porta id leo.

	// Praesent consequat, turpis rhoncus eleifend viverra, nisi dolor malesuada augue, sed venenatis risus ipsum sit amet metus. Nam et egestas purus. Nunc nibh elit, luctus id cursus non, commodo vel massa. Ut et massa lobortis, venenatis lectus eu, suscipit tellus. Phasellus arcu sem, venenatis id eros quis, hendrerit convallis mi. Nunc vitae tristique elit, a euismod orci. Mauris massa purus, suscipit vel mi at, finibus dapibus nunc. Praesent placerat molestie nulla eu posuere. Proin sit amet velit eget nulla molestie malesuada. In sagittis odio porttitor felis luctus, vitae eleifend ipsum rhoncus. Aliquam ac tortor est. Ut nec imperdiet odio. Maecenas tincidunt elit a augue facilisis viverra. Morbi massa lacus, dictum vitae elit sit amet, molestie porttitor est.

	// Sed vel tortor dapibus, viverra massa ac, aliquet nulla. Fusce interdum efficitur placerat. Integer placerat pulvinar libero vitae facilisis. Sed arcu nulla, sagittis non quam et, malesuada finibus ante. Sed fringilla odio non lobortis elementum. Ut euismod tincidunt mauris, at suscipit libero fermentum nec. Vestibulum sit amet dui augue. Mauris lobortis, nisi iaculis placerat accumsan, odio massa elementum ligula, at consequat neque erat at mi. Pellentesque velit lacus, commodo ac dui nec, fringilla dictum lorem. Phasellus quis nisl nec turpis tincidunt viverra suscipit nec quam. Nullam at urna aliquam, imperdiet massa at, vestibulum urna. Suspendisse vitae maximus dui, eu pulvinar sapien. Aenean ut neque dignissim, vulputate sapien ut, interdum erat. Sed mollis mi non lorem viverra bibendum. Vivamus vitae euismod purus.

	// Suspendisse eleifend risus massa, in volutpat dui varius in. Nulla egestas lorem a eros posuere maximus. Aliquam ut diam leo. Donec non metus congue, blandit sem a, consequat velit. Donec at consequat sem. Nullam pulvinar id velit et auctor. Phasellus ut odio eget lorem accumsan rutrum vitae non arcu. Curabitur pulvinar libero in neque rutrum porttitor. Fusce efficitur orci ut diam suscipit, eu rutrum elit consectetur.

	// Maecenas metus nulla, pellentesque eget mollis a, venenatis eget lectus. Duis id ligula sagittis neque volutpat rutrum feugiat vel enim. Pellentesque volutpat nisi eleifend, viverra dolor dapibus, suscipit dolor. Phasellus vitae aliquet leo. Nulla quis neque tempor, posuere metus quis, ornare arcu. Nullam dolor diam, tincidunt at magna non, venenatis.`,
	// 	},
];
