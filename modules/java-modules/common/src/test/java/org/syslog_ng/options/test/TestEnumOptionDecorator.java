/*
 * Copyright (c) 2015 Balabit
 * Copyright (c) 2015 Viktor Juhasz <viktor.juhasz@balabit.com>
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 * As an additional exemption you are allowed to compile & link against the
 * OpenSSL libraries as published by the OpenSSL project. See the file
 * COPYING for details.
 *
 */

package org.syslog_ng.options.test;

import static org.junit.Assert.*;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

import org.junit.Before;
import org.junit.Test;
import org.syslog_ng.options.EnumOptionDecorator;
import org.syslog_ng.options.Option;
import org.syslog_ng.options.StringOption;

public class TestEnumOptionDecorator extends TestOption {


	@Before
	public void setUp() throws Exception {
		super.setUp();
		options.put("cluster", "syslog-ng");
	}

	@Test
	public void testNormal() {
		Option stringOption = new StringOption(owner, "cluster");
		Set<String> values = new HashSet<String>(Arrays.asList("syslog-ng", "test"));
		Option enumdecorator = new EnumOptionDecorator(stringOption, values);
		assertInitOptionSuccess(enumdecorator);

		options.put("cluster", "test");
		assertInitOptionSuccess(enumdecorator);
	}

	@Test
	public void testInvalidOption() {
		Option stringOption = new StringOption(owner, "cluster");
		Set<String> values = new HashSet<String>(Arrays.asList("syslog-ng", "test"));
		Option enumdecorator = new EnumOptionDecorator(stringOption, values);

		options.put("cluster", "invalid");
		assertInitOptionFailed(enumdecorator,
				"option cluster must be one of the following values");

		options.remove("cluster");
		assertEquals(null, stringOption.getValue());
		assertInitOptionFailed(enumdecorator,
				"option cluster must be one of the following values");
	}
}
